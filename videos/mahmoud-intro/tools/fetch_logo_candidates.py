"""Download logo candidates for each company in logo-sources.tsv.

For every row (key, page URLs, Wikimedia Commons search term, optional keyword) this
saves, under assets/logos/_candidates/<key>/, each page's icons, og:image, <img> files
that look like a logo (or mention the keyword), inline <svg> logos, and the top
Wikimedia Commons "<term> logo" files. Lines starting with # are ignored.
A person then reviews the candidates and keeps the real logo. Runs in GitHub Actions
(the build machine has open internet access).
"""

import html.parser
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = os.path.join(ROOT, "tools", "logo-sources.tsv")
OUT = os.path.join(ROOT, "assets", "logos", "_candidates")
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
MAX_PER_SITE = 8


def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.headers.get("Content-Type", ""), resp.geturl()


class LogoParser(html.parser.HTMLParser):
    def __init__(self, keyword=""):
        super().__init__()
        self.keyword = keyword.lower()
        self.urls = []
        self.svgs = []
        self._svg_depth = 0
        self._svg_buf = []
        self._svg_is_logo = False

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        blob = " ".join(a.values()).lower()
        wanted = "logo" in blob or (self.keyword and self.keyword in blob)
        if tag == "link" and re.search(r"icon", a.get("rel", ""), re.I) and a.get("href"):
            self.urls.append(a["href"])
        elif tag == "meta" and a.get("property", a.get("name", "")).lower() in ("og:image", "twitter:image") and a.get("content"):
            self.urls.append(a["content"])
        elif tag == "img" and wanted:
            for k in ("src", "data-src", "data-lazy-src"):
                if a.get(k) and not a[k].startswith("data:"):
                    self.urls.append(a[k])
                    break
        if tag == "svg":
            if self._svg_depth == 0:
                self._svg_buf = []
                self._svg_is_logo = wanted
            self._svg_depth += 1
        if self._svg_depth:
            # The raw tag keeps case-sensitive SVG attributes such as viewBox.
            self._svg_buf.append(self.get_starttag_text())

    def handle_startendtag(self, tag, attrs):
        if self._svg_depth:
            self._svg_buf.append(self.get_starttag_text())
        else:
            self.handle_starttag(tag, attrs)
            if tag == "svg":
                self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self._svg_depth:
            self._svg_buf.append(f"</{tag}>")
            if tag == "svg":
                self._svg_depth -= 1
                if self._svg_depth == 0 and self._svg_is_logo:
                    svg = "".join(self._svg_buf)
                    if 'xmlns="http://www.w3.org/2000/svg"' not in svg:
                        svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
                    self.svgs.append(svg)

    def handle_data(self, data):
        if self._svg_depth:
            self._svg_buf.append(data)


def ext_for(url, ctype):
    path = urllib.parse.urlparse(url).path.lower()
    for e in (".svg", ".png", ".webp", ".jpg", ".jpeg", ".ico", ".gif"):
        if path.endswith(e):
            return e
    for k, e in (("svg", ".svg"), ("png", ".png"), ("webp", ".webp"), ("jpeg", ".jpg"), ("icon", ".ico"), ("gif", ".gif")):
        if k in ctype:
            return e
    return ".bin"


def save(folder, name, data):
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, name), "wb") as f:
        f.write(data)


def from_site(key, pages, keyword, folder, log):
    n = s = 0
    for page in pages:
        try:
            body, _, final = get(page)
        except Exception as e:  # noqa: BLE001 - report and try the next URL
            log.append(f"{key}: {page} failed: {e}")
            continue
        p = LogoParser(keyword)
        p.feed(body.decode("utf-8", "replace"))
        seen, got = set(), 0
        for u in p.urls:
            full = urllib.parse.urljoin(final, u)
            if full in seen:
                continue
            seen.add(full)
            try:
                data, ctype, _ = get(full)
            except Exception as e:  # noqa: BLE001
                log.append(f"{key}: {full} failed: {e}")
                continue
            n += 1
            got += 1
            save(folder, f"site-{n:02d}{ext_for(full, ctype)}", data)
            log.append(f"{key}: site-{n:02d} <- {full}")
            if got >= MAX_PER_SITE:
                break
        for svg in p.svgs[:3]:
            s += 1
            save(folder, f"inline-{s:02d}.svg", svg.encode())
            log.append(f"{key}: inline-{s:02d}.svg <- inline <svg> on {final}")


def from_commons(key, term, folder, log):
    time.sleep(3)  # Wikimedia rate-limits bursts of requests
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
        "gsrsearch": f"{term} logo", "gsrlimit": 3, "prop": "imageinfo", "iiprop": "url",
    })
    try:
        data, _, _ = get(f"https://commons.wikimedia.org/w/api.php?{q}")
        pages = json.loads(data).get("query", {}).get("pages", {})
    except Exception as e:  # noqa: BLE001
        log.append(f"{key}: commons search failed: {e}")
        return
    for i, page in enumerate(sorted(pages.values(), key=lambda p: p.get("index", 0)), 1):
        url = page.get("imageinfo", [{}])[0].get("url")
        if not url:
            continue
        try:
            img, ctype, _ = get(url)
        except Exception as e:  # noqa: BLE001
            log.append(f"{key}: {url} failed: {e}")
            continue
        save(folder, f"commons-{i:02d}{ext_for(url, ctype)}", img)
        log.append(f"{key}: commons-{i:02d} <- {page.get('title')} {url}")


def main():
    log = []
    with open(SOURCES, encoding="utf-8") as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            cols = line.rstrip("\n").split("\t")
            key, pages, term = cols[:3]
            keyword = cols[3] if len(cols) > 3 else ""
            folder = os.path.join(OUT, key)
            from_site(key, pages.split(), keyword, folder, log)
            from_commons(key, term, folder, log)
    if not log:
        print("No logos listed to fetch.")
        return
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "SOURCES.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    sys.exit(main())
