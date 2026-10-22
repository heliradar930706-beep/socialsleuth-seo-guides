# Building a Static Instagram Story Viewer Front End with Hugging Face Spaces

A practical guide to HTML, JavaScript input handling, and a clean handoff from a static landing page to a production web application.

**Live case study:** [SocialSleuth's Anonymous Instagram Story Viewer on Hugging Face](https://huggingface.co/spaces/SocialSleuth/Instagram-story-viewer)

## 1. Why a static Space?

A public, shareable tool landing page does not need to copy an application's entire backend. Hugging Face **Static HTML Spaces** can host an HTML/CSS/JavaScript introduction while a separate service handles verification, quotas, public-data requests and media display.

In SocialSleuth's case, the Space introduces an Instagram Story viewer, accepts a username or public Instagram profile URL, explains verification, and directs visitors toward the connected product. This repository does **not** contain the private lookup backend.

The architecture to aim for:

~~~text
Visitor
  -> Static Hugging Face Space
       - clear UI and explanations
       - local input format validation
  -> Your existing application
       - server-side validation and verification
       - rate limits and public-data lookups
       - eligible Story media, downloads and optional archive
~~~

A static page alone cannot enforce a secure rate limit or hide provider API keys.

## 2. Configure a Static HTML Space

Create a Space with the **Static** SDK. A minimal repository has a README.md and index.html. The Space's own README.md begins with YAML frontmatter:

~~~yaml
---
title: Public Story Viewer Demo
emoji: 👀
colorFrom: purple
colorTo: blue
sdk: static
app_file: index.html
short_description: Static landing page for a public Story Viewer
---
~~~

This configuration is an **illustrative new Space**, not a proposal to replace SocialSleuth's working Space. The frontmatter must start at the top of the Space README, and the named index.html file must exist.

Official reference: [Hugging Face Static HTML Spaces](https://huggingface.co/docs/hub/spaces-sdks-static).

## 3. Create a small, accurate page

A minimal index.html can introduce the public tool and link to an existing viewer without falsely claiming to fetch Instagram content in the browser:

~~~html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Public Instagram Story Viewer</title>
  <meta name="description" content="Discover a viewer for currently public Instagram Stories.">
</head>
<body>
  <main>
    <h1>View currently public Instagram Stories</h1>
    <p>Public profiles only. An Instagram sign-in is not required.</p>
    <a href="https://huggingface.co/spaces/SocialSleuth/Instagram-story-viewer">Open the SocialSleuth viewer demo</a>
  </main>
</body>
</html>
~~~

This is teaching markup, **not the exact source code of the production Space**. Give inputs and buttons accessible labels and make navigation work by keyboard. State that private and expired Stories are not available.

## 4. Accept usernames or profile links without guessing

People paste several forms of input: **example_user**, **@example_user**, or a full Instagram profile URL. Normalize this input before sending it to an application.

This repository has a focused, testable parser:

- [examples/instagram-username.mjs](../examples/instagram-username.mjs)
- [examples/instagram-username.test.mjs](../examples/instagram-username.test.mjs)

Example use:

~~~js
import { normalizeInstagramUsername } from "../examples/instagram-username.mjs";

normalizeInstagramUsername("@Example.User");
// "example.user"

normalizeInstagramUsername("https://www.instagram.com/example_user/?hl=en");
// "example_user"

normalizeInstagramUsername("https://www.instagram.com/stories/example_user/");
// null — a Story URL is not a profile URL
~~~

The code checks a small allowlist of Instagram hostnames, requires exactly one profile path segment, and validates the username's shape. It rejects common reserved paths like stories, p and reel. It **does not** establish that an account exists, that it is public, or that current Stories are available.

This is convenience validation. Repeat checks on the server before any production lookup.

## 5. Route to the production application safely

A sensible handoff is:

1. Validate the input in the browser for quick feedback.
2. Use the destination application's **documented** URL or API contract.
3. Revalidate on the server; do not trust client validation alone.
4. Perform any bot verification and rate-limit enforcement on the server.
5. Process only public content the application is authorized to access.

Do not invent query-string parameters that the destination application may not support. The published [SocialSleuth Space](https://huggingface.co/spaces/SocialSleuth/Instagram-story-viewer) is the confirmed public starting point; this tutorial intentionally does not assert how its private routing contract works.

Do not expose Instagram passwords, provider tokens, archive credentials, or private API secrets in front-end HTML or JavaScript.

## 6. Test and deploy

From the root of this GitHub repository, with Node.js 18+:

~~~bash
node --test examples/instagram-username.test.mjs
~~~

For your own Static Space, commit README.md and index.html to the Space repository and check the rendered page. Test invalid input, navigation, keyboard access, and mobile layouts. If you use a framework, Hugging Face also supports optional build commands and serving the generated HTML.

## 7. What the live SocialSleuth example actually offers

The [SocialSleuth Anonymous Instagram Story Viewer Space](https://huggingface.co/spaces/SocialSleuth/Instagram-story-viewer) advertises a public-only, no-Instagram-login viewing workflow. Visitors are told to enter a public username or profile link and complete a verification step. The connected [SocialSleuth Story Viewer](https://www.socialsleuth.xyz/instagram-story-viewer) is where the actual service and optional monitoring features live.

A public Story may not be available if the account is private, no active Story exists, or the Story has expired. Neither static hosting nor a GitHub README changes those limits.

## Key takeaway

Use Hugging Face Spaces for a useful demonstration and clear product entry point, while keeping verification, sensitive operations and data requests in the application that owns them. Include runnable examples and accurate limitations rather than disguising a landing page as an open-source scraper.

---

**Disclosure:** This guide is published by SocialSleuth and links to its own service. SocialSleuth is not affiliated with Instagram or Meta. Respect privacy, copyright, laws and applicable platform terms.
