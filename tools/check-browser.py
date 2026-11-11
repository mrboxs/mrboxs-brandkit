#!/usr/bin/env python3
"""Exercise the supplied CSS and theme adapter in headless Chromium, without a server."""
import base64
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
chrome = shutil.which("chromium") or shutil.which("google-chrome")
if not chrome:
    raise SystemExit("Chromium is required for this optional integration check.")

css = (ROOT / "04-brand/brand.css").as_uri()
script = (ROOT / "02-icons/web/theme-sync.js").as_uri()
favicon = (ROOT / "02-icons/web/favicon.svg").as_uri()
image = base64.b64encode((ROOT / "02-icons/web/favicon.svg").read_bytes()).decode()
page = f'''<!doctype html><html lang="en"><head><title>Brand integration check</title>
<link rel="stylesheet" href="{css}"><link id="mrboxs-favicon" rel="icon" href="{favicon}">
<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)">
<script src="{script}" defer></script></head><body><main>
<span class="mrboxs-logo"><img class="mrboxs-logo--light" alt=""><img class="mrboxs-logo--dark" alt=""></span>
<pre id="result">pending</pre></main><script>
window.addEventListener('load', async () => {{
  const results = [];
  const root = document.documentElement;
  const isDark = matchMedia('(prefers-color-scheme: dark)').matches;
  function check(ok, name) {{ if (!ok) throw new Error(name); results.push(name); }}
  const tick = () => new Promise(resolve => setTimeout(resolve, 40));
  const style = () => getComputedStyle(root);
  try {{
    check(style().getPropertyValue('--mrboxs-bg').trim() === (isDark ? '#000' : '#fff'), 'Initial OS theme');
    for (const theme of ['dark', 'light', 'system']) {{
      root.dataset.theme = theme;
      await tick();
      const dark = theme === 'dark' || (theme === 'system' && isDark);
      check(style().getPropertyValue('--mrboxs-fg').trim() === (dark ? '#fff' : '#000'), theme + ': CSS foreground');
      const light = document.querySelector('.mrboxs-logo--light');
      const darkImg = document.querySelector('.mrboxs-logo--dark');
      check((getComputedStyle(light).display === 'none') === dark, theme + ': light artwork visibility');
      check((getComputedStyle(darkImg).display !== 'none') === dark, theme + ': dark artwork visibility');
      check(document.getElementById('mrboxs-favicon').href.endsWith(theme === 'system' ? '/web/favicon.svg' : '/web/' + theme + '/favicon.svg'), theme + ': favicon URL');
      for (const meta of document.querySelectorAll('meta[name="theme-color"]')) {{
        if (theme === 'system') check(meta.media.includes('prefers-color-scheme'), 'Restored media query');
        else check(!meta.media && meta.content === (dark ? '#000000' : '#FFFFFF'), theme + ': browser chrome');
      }}
    }}
    delete root.dataset.theme;
    await tick();
    const img = new Image();
    img.src = 'data:image/svg+xml;base64,{image}';
    await img.decode();
    const canvas = document.createElement('canvas'); canvas.width = canvas.height = 32;
    const ctx = canvas.getContext('2d'); ctx.drawImage(img, 0, 0);
    const pixel = ctx.getImageData(2, 16, 1, 1).data;
    check(pixel[0] === (isDark ? 0 : 255), 'Adaptive SVG surface matches OS theme');
    check(pixel[3] === 255, 'Adaptive SVG rendered opaque tile');
    document.getElementById('result').textContent = JSON.stringify({{status:'PASS', osTheme:isDark?'dark':'light', checks:results}});
  }} catch (e) {{ document.getElementById('result').textContent = JSON.stringify({{status:'FAIL', error:String(e), checks:results}}); }}
}});
</script></body></html>'''

reports = []
with tempfile.TemporaryDirectory(prefix="mrboxs-browser-") as temp:
    page_path = Path(temp) / "check.html"
    page_path.write_text(page)
    for dark in (False, True):
        cmd = [chrome, "--headless", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--allow-file-access-from-files", f"--user-data-dir={temp}/profile-{'dark' if dark else 'light'}", "--virtual-time-budget=3000", "--dump-dom"]
        if dark:
            cmd.append("--force-dark-mode")
        result = subprocess.run(cmd + [page_path.as_uri()], capture_output=True, text=True, timeout=30)
        match = re.search(r'<pre id="result">(.*?)</pre>', result.stdout, re.S)
        if not match:
            raise RuntimeError(f"No browser results: {result.stderr[-1000:]}")
        report = json.loads(html.unescape(match.group(1)))
        assert report["status"] == "PASS", report
        assert report["osTheme"] == ("dark" if dark else "light"), report
        reports.append(report)
(ROOT / "05-guidelines/browser-verification.json").write_text(json.dumps({"status": "PASS", "browser": subprocess.run([chrome, "--version"], capture_output=True, text=True).stdout.strip(), "runs": reports}, indent=2) + "\n")
for report in reports:
    print(f'PASS: Chromium OS {report["osTheme"]}, {len(report["checks"])} assertions, CSS + manual theme + adaptive SVG.')
