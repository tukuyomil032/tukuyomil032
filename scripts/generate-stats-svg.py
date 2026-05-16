#!/usr/bin/env python3
"""
Fetches GitHub stats card SVGs and combines them into a single
self-contained SVG file (assets/profile/stats-layout-v2.svg).
Both cards are displayed side by side at equal height.
"""
import os
import re
import urllib.request

STATS_URL = (
    "https://github-readme-stats-eight-fawn-62.vercel.app/api"
    "?username=tukuyomil032"
    "&show_icons=true"
    "&theme=prussian"
    "&count_private=true"
    "&include_all_commits=false"
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
OUTPUT = "assets/profile/stats-layout-v2.svg"
GAP = 10


def fetch_svg(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse_svg(raw, svg_id):
    viewbox_m = re.search(r'viewBox="([^"]+)"', raw)
    viewbox = viewbox_m.group(1) if viewbox_m else "0 0 460 175"
    vb_parts = viewbox.split()
    vb_width = round(float(vb_parts[2])) if len(vb_parts) >= 3 else 460
    vb_height = round(float(vb_parts[3])) if len(vb_parts) >= 4 else 175

    height_m = re.search(r'<svg[^>]+height="([^"]+)"', raw)
    height = round(float(height_m.group(1))) if height_m else vb_height

    inner = re.sub(r"^<svg[^>]*>", "", raw.strip(), count=1)
    inner = re.sub(r"</svg>\s*$", "", inner)

    return {
        "id": svg_id,
        "vb_width": vb_width,
        "vb_height": vb_height,
        "height": height,
        "inner": inner,
    }


def main():
    print("Fetching stats card…")
    stats = parse_svg(fetch_svg(STATS_URL), "stats-card")
    print(f"  vb={stats['vb_width']}x{stats['vb_height']} height={stats['height']}")

    print("Fetching langs card…")
    langs = parse_svg(fetch_svg(LANGS_URL), "langs-card")
    print(f"  vb={langs['vb_width']}x{langs['vb_height']} height={langs['height']}")

    # Both cards rendered at the same display height so borders align.
    # Setting viewBox height = display_height avoids preserveAspectRatio gaps.
    display_h = max(stats["height"], langs["height"])
    total_w = stats["vb_width"] + GAP + langs["vb_width"]
    langs_x = stats["vb_width"] + GAP

    svg = f"""\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w} {display_h}" width="100%">
  <svg id="stats-card"
       x="0" y="0" width="{stats['vb_width']}" height="{display_h}"
       viewBox="0 0 {stats['vb_width']} {display_h}" xmlns="http://www.w3.org/2000/svg">
    {stats['inner']}
  </svg>
  <svg id="langs-card"
       x="{langs_x}" y="0" width="{langs['vb_width']}" height="{display_h}"
       viewBox="0 0 {langs['vb_width']} {display_h}" xmlns="http://www.w3.org/2000/svg">
    {langs['inner']}
  </svg>
</svg>
"""

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Written: {OUTPUT}")


if __name__ == "__main__":
    main()
