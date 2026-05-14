#!/usr/bin/env python3
"""
Fetches GitHub stats card SVGs and combines them into a single
self-contained responsive SVG with CSS media queries.
Mobile (<601px): stacked vertically, each card at 100% width.
Desktop (>=601px): side by side, each card at 50% width.
"""
import re
import sys
import urllib.request

STATS_URL = (
    "https://github-readme-stats-eight-fawn-62.vercel.app/api"
    "?username=tukuyomil032"
    "&show_icons=true"
    "&theme=prussian"
    "&count_private=true"
    "&include_all_commits=true"
)
LANGS_URL = (
    "https://github-readme-stats-eight-fawn-62.vercel.app/api/top-langs"
    "?username=tukuyomil032"
    "&layout=compact"
    "&langs_count=8"
    "&card_width=460"
    "&theme=prussian"
    "&hide=php,scss,css,markdown,mdx,javascript,vue,kotlin"
)
OUTPUT = "assets/profile/stats-layout.svg"


def fetch_svg(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse_svg(raw, svg_id):
    viewbox_m = re.search(r'viewBox="([^"]+)"', raw)
    viewbox = viewbox_m.group(1) if viewbox_m else "0 0 460 175"

    height_m = re.search(r'<svg[^>]+height="([^"]+)"', raw)
    height = round(float(height_m.group(1))) if height_m else 175

    inner = re.sub(r"^<svg[^>]*>", "", raw.strip(), count=1)
    inner = re.sub(r"</svg>\s*$", "", inner)

    return {"id": svg_id, "viewbox": viewbox, "height": height, "inner": inner}


def main():
    print("Fetching stats card…")
    stats = parse_svg(fetch_svg(STATS_URL), "stats-card")
    print(f"  viewBox={stats['viewbox']} height={stats['height']}")

    print("Fetching langs card…")
    langs = parse_svg(fetch_svg(LANGS_URL), "langs-card")
    print(f"  viewBox={langs['viewbox']} height={langs['height']}")

    gap = 10
    mobile_h = stats["height"] + gap + langs["height"]
    desktop_h = max(stats["height"], langs["height"])
    langs_y = stats["height"] + gap

    svg = f"""\
<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{mobile_h}">
  <style>
    /* Desktop (>=601px): side by side */
    @media (min-width: 601px) {{
      :root {{ height: {desktop_h}px; }}
      svg#{stats['id']} {{ width: 50%; }}
      svg#{langs['id']} {{ x: 50%; y: 0; width: 50%; }}
    }}
  </style>

  <svg id="{stats['id']}"
       x="0" y="0" width="100%" height="{stats['height']}"
       viewBox="{stats['viewbox']}" xmlns="http://www.w3.org/2000/svg">
    {stats['inner']}
  </svg>

  <svg id="{langs['id']}"
       x="0" y="{langs_y}" width="100%" height="{langs['height']}"
       viewBox="{langs['viewbox']}" xmlns="http://www.w3.org/2000/svg">
    {langs['inner']}
  </svg>
</svg>
"""

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Written: {OUTPUT}")


if __name__ == "__main__":
    main()
