import test from "node:test";
import assert from "node:assert/strict";
import { normalizeInstagramUsername } from "./instagram-username.mjs";

test("normalizes handles and supported Instagram profile URLs", () => {
  assert.equal(normalizeInstagramUsername("@Example.User"), "example.user");
  assert.equal(normalizeInstagramUsername(" https://www.instagram.com/Example.User/?hl=en "), "example.user");
  assert.equal(normalizeInstagramUsername("instagram.com/example_user/"), "example_user");
  assert.equal(normalizeInstagramUsername("m.instagram.com/my.user"), "my.user");
});

test("rejects non-profile URLs and invalid usernames", () => {
  assert.equal(normalizeInstagramUsername("https://www.instagram.com/stories/someone/"), null);
  assert.equal(normalizeInstagramUsername("https://evil.example/someone"), null);
  assert.equal(normalizeInstagramUsername("@bad handle"), null);
  assert.equal(normalizeInstagramUsername(""), null);
  assert.equal(normalizeInstagramUsername("A".repeat(31)), null);
  assert.equal(normalizeInstagramUsername("foo..bar"), null);
  assert.equal(normalizeInstagramUsername(".abc"), null);
  assert.equal(normalizeInstagramUsername("abc."), null);
  assert.equal(normalizeInstagramUsername("https://instagram.com/p/abc"), null);
});
