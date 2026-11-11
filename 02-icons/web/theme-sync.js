/* Optional adapter for <html data-theme="light|dark|system">. No storage or UI. */
(() => {
  const root = document.documentElement;
  const system = window.matchMedia("(prefers-color-scheme: dark)");
  const favicon = document.getElementById("mrboxs-favicon");
  if (!favicon) return;
  // Resolve siblings from the supplied icon URL, so subpath deployments also work.
  const base = new URL(".", favicon.href);
  function sync() {
    const chosen = root.dataset.theme;
    const explicit = chosen === "light" || chosen === "dark";
    const resolved = explicit ? chosen : system.matches ? "dark" : "light";
    favicon.href = new URL(explicit ? `${resolved}/favicon.svg` : "favicon.svg", base).href;
    document.querySelectorAll('meta[name="theme-color"]').forEach(meta => {
      // The app's explicit preference takes precedence over media queries.
      if (explicit) {
        meta.removeAttribute("media");
        meta.content = resolved === "dark" ? "#000000" : "#FFFFFF";
      } else {
        const dark = meta.dataset.mrboxsMedia === "dark";
        meta.media = `(prefers-color-scheme: ${dark ? "dark" : "light"})`;
        meta.content = dark ? "#000000" : "#FFFFFF";
      }
    });
  }
  document.querySelectorAll('meta[name="theme-color"]').forEach(meta => {
    meta.dataset.mrboxsMedia = meta.media.includes("dark") ? "dark" : "light";
  });
  new MutationObserver(sync).observe(root, { attributes: true, attributeFilter: ["data-theme"] });
  system.addEventListener("change", sync);
  sync();
})();
