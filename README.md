# SocialSleuth Guides

Practical guides and small code examples for public Instagram Story viewing tools.

## Anonymous Instagram Story Viewer — live demo

**[Open the SocialSleuth Instagram Story Viewer on Hugging Face Spaces](https://huggingface.co/spaces/SocialSleuth/Instagram-story-viewer)**

The Space is a browser-based entry point for exploring **currently available Stories from public Instagram accounts**. Visitors can enter a public Instagram username or profile URL, complete the required verification, and continue to the connected SocialSleuth viewer.

- Public accounts only; private and restricted Stories are not available.
- No Instagram login is required for the public Story lookup.
- Available public Stories can be viewed and downloaded in the connected experience.
- The live page currently describes a free allowance of three distinct public usernames per UTC day; limits may change.

**[Use the full Story Viewer on SocialSleuth](https://www.socialsleuth.xyz/instagram-story-viewer)**.

The Hugging Face Space is a static landing/entry page. Verification, quotas, Story retrieval and any archiving are handled by the connected service, not by this GitHub repository.

## Technical tutorial

**[Build a static Instagram Story Viewer front end with Hugging Face Spaces](docs/static-instagram-story-viewer-on-hugging-face.md)**

This hands-on tutorial explains Static HTML Spaces, a minimal deployment configuration, accessibility and privacy boundaries, input normalization, and the separation between a static page and a production service.

### Runnable JavaScript example

- [Instagram username/profile URL normalizer](examples/instagram-username.mjs)
- [Node.js tests](examples/instagram-username.test.mjs)

From the repository root with Node.js 18+:

~~~bash
node --test examples/instagram-username.test.mjs
~~~

The example accepts plain handles, @handles, and Instagram profile links. It rejects unsupported Story, post, or Reel URLs instead of pretending they are usernames.

## More public resources

- [Comparison of anonymous Instagram Story viewers](index.html)
- [Instagram activity tracker guide](instagram-activity-trackers-2026/index.html)
- [Hugging Face's official Static HTML Spaces documentation](https://huggingface.co/docs/hub/spaces-sdks-static)

## Disclosure and limitations

This public repository is operated by SocialSleuth and links to its own product. It is **not** the SocialSleuth production backend, an Instagram scraper, or a tool to access private profiles. The included JavaScript is an independent educational example, not a copy of proprietary implementation. Do not put secrets in static client-side code.

SocialSleuth is not affiliated with Instagram or Meta. Respect privacy, copyright, applicable law, and third-party platform terms.
