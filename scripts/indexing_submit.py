#!/usr/bin/env python3
"""Send Indexing API URL_UPDATED notices for a monitored sitemap or manual URLs.

Google officially permits Indexing API for JobPosting and certain live BroadcastEvent
pages only. A successful API acknowledgement is not proof that a URL is indexed.
"""
import gzip
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET

import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

INDEXING_SCOPE = "https://www.googleapis.com/auth/indexing"
STATE_FILE = Path(".indexing-state.json")
MAX_PER_RUN = 20
MAX_PER_DAY = 180
MAX_SITEMAPS = 60


def valid_url(value):
    parts = urlsplit(value)
    return parts.scheme == "https" and bool(parts.netloc) and not parts.username


def read_state():
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        return {
            "submitted": data.get("submitted", {}),
            "day": data.get("day", ""),
            "count": int(data.get("count", 0)),
        }
    except (FileNotFoundError, OSError, ValueError, TypeError):
        return {"submitted": {}, "day": "", "count": 0}


def save_state(state):
    temporary = STATE_FILE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, sort_keys=True, indent=2), encoding="utf-8")
    temporary.replace(STATE_FILE)


def text_of_child(element, child_name):
    for child in element:
        if child.tag.rsplit("}", 1)[-1] == child_name:
            return (child.text or "").strip()
    return ""


def sitemap_entries(sitemap_url, session, visited):
    if sitemap_url in visited or len(visited) >= MAX_SITEMAPS:
        return
    visited.add(sitemap_url)
    response = session.get(sitemap_url, timeout=25, headers={
        "User-Agent": "SocialSleuth-Indexing-Automation/1.0"
    })
    response.raise_for_status()
    data = response.content
    if data.startswith(b"\x1f\x8b"):
        data = gzip.decompress(data)
    root = ET.fromstring(data)
    root_type = root.tag.rsplit("}", 1)[-1]
    if root_type == "sitemapindex":
        for element in root:
            if element.tag.rsplit("}", 1)[-1] != "sitemap":
                continue
            child = text_of_child(element, "loc")
            if valid_url(child):
                yield from sitemap_entries(child, session, visited)
    elif root_type == "urlset":
        for element in root:
            if element.tag.rsplit("}", 1)[-1] != "url":
                continue
            url = text_of_child(element, "loc")
            if valid_url(url):
                yield url, text_of_child(element, "lastmod")
    else:
        raise ValueError("Unsupported sitemap format: " + root_type)


def indexing_service():
    raw_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip()
    if not raw_json:
        raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT_JSON Actions secret.")
    account = json.loads(raw_json)
    credentials = service_account.Credentials.from_service_account_info(
        account, scopes=[INDEXING_SCOPE]
    )
    return build("indexing", "v3", credentials=credentials, cache_discovery=False)


def main():
    state = read_state()
    today = datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    if state["day"] != today:
        state["day"], state["count"] = today, 0

    sitemap_input = os.getenv("INDEXING_SITEMAPS", "").strip()
    manual_input = os.getenv("INDEXING_URLS", "").strip()
    if not sitemap_input and not manual_input:
        raise RuntimeError("Provide INDEXING_SITEMAPS variable or manual workflow URLs.")

    candidates = {}
    if sitemap_input:
        with requests.Session() as session:
            visited = set()
            for sitemap in sitemap_input.replace("\n", ",").split(","):
                sitemap = sitemap.strip()
                if not sitemap:
                    continue
                if not valid_url(sitemap):
                    raise ValueError("Invalid HTTPS sitemap: " + sitemap)
                for url, lastmod in sitemap_entries(sitemap, session, visited):
                    candidates[url] = "lastmod:" + lastmod if lastmod else "new-url"

    manual_urls = [v.strip() for v in manual_input.replace("\n", ",").split(",") if v.strip()]
    for url in manual_urls:
        if not valid_url(url):
            raise ValueError("Invalid manual HTTPS URL: " + url)
        candidates[url] = "manual:" + today + ":" + str(int(time.time()))

    pending = [(url, stamp) for url, stamp in candidates.items()
               if state["submitted"].get(url) != stamp]
    capacity = max(0, min(MAX_PER_RUN, MAX_PER_DAY - state["count"]))
    print(f"URLs scanned={len(candidates)}; new/changed={len(pending)}; allowance={capacity}")
    if not pending or not capacity:
        save_state(state)
        return 0

    service = indexing_service()
    accepted = 0
    failed = 0
    for url, stamp in pending[:capacity]:
        try:
            response = service.urlNotifications().publish(body={
                "url": url, "type": "URL_UPDATED"
            }).execute()
            state["submitted"][url] = stamp
            state["count"] += 1
            accepted += 1
            print("ACCEPTED", url, response.get("urlNotificationMetadata", {}).get("url", ""))
        except HttpError as error:
            failed += 1
            status = getattr(error.resp, "status", "unknown")
            print(f"API_ERROR status={status} url={url}: {error}", file=sys.stderr)
            if status in (403, 429):
                print("Stopping on authorization/quota error.", file=sys.stderr)
                break
        finally:
            save_state(state)
    print(f"Finished: accepted={accepted}, failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print("FATAL:", error, file=sys.stderr)
        sys.exit(1)
