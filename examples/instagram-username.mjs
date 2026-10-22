/**
 * Normalize Instagram username input for a public-profile UI.
 * Accepts plain handles, @handles and standard Instagram profile URLs.
 * Returns a lower-case username or null.
 * This does not check account existence, privacy or Story availability.
 */
function normalizeInstagramUsername(input) {
  if (typeof input !== "string") return null;
  let candidate = input.trim();
  if (candidate.startsWith("@")) candidate = candidate.slice(1);
  const isUrl = /^https?:\/\//i.test(candidate) ||
    /^(?:www\.|m\.)?instagram\.com(?:\/|$)/i.test(candidate);
  if (isUrl) {
    try {
      const full = /^https?:\/\//i.test(candidate) ? candidate : "https://" + candidate;
      const url = new URL(full);
      const allowedHosts = new Set(["instagram.com", "www.instagram.com", "m.instagram.com"]);
      if (!allowedHosts.has(url.hostname.toLowerCase()) || url.username || url.password || url.port) return null;
      const segments = url.pathname.split("/").filter(Boolean);
      if (segments.length !== 1) return null;
      candidate = segments[0];
    } catch {
      return null;
    }
  }
  const reserved = new Set(["accounts", "about", "direct", "explore", "p", "reel", "reels", "stories", "tv"]);
  if (!/^[A-Za-z0-9._]{1,30}$/.test(candidate) ||
      candidate.startsWith(".") || candidate.endsWith(".") ||
      candidate.includes("..") || reserved.has(candidate.toLowerCase())) return null;
  return candidate.toLowerCase();
}

export { normalizeInstagramUsername };
