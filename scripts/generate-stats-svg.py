#!/usr/bin/env python3
"""
Fetches GitHub stats card SVGs and embeds them as INLINE SVG in README.md.

Inline SVG (not via <img>) allows @media queries to respond to the browser's
actual document viewport width — enabling true responsive layout:
  Mobile  (<600px viewport): cards stacked vertically at 100% width
  Desktop (>=600px viewport): cards side by side at 50% width each
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
README = "README.md"
MARKER_START = "<!-- STATS-START -->"
MARKER_END = "<!-- STATS-END -->"


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
    card_h = max(stats["height"], langs["height"])
    langs_y = stats["height"] + gap
    mobile_h = stats["height"] + gap + langs["height"]

    inline_svg = f"""\
{MARKER_START}
<svg id="stats-layout" xmlns="http://www.w3.org/2000/svg" width="100%">
  <style>
    /* Mobile default: stacked */
    #stats-layout {{ height: {mobile_h}px; }}
    svg#stats-card {{ x: 0; y: 0; width: 100%; height: {stats['height']}px; }}
    svg#langs-card {{ x: 0; y: {langs_y}px; width: 100%; height: {langs['height']}px; }}
    /* Desktop (>=600px): side by side */
    @media (min-width: 600px) {{
      #stats-layout {{ height: {card_h}px; }}
      svg#stats-card {{ width: 50%; }}
      svg#langs-card {{ x: 50%; y: 0; width: 50%; }}
    }}
  </style>
  <svg id="stats-card"
       x="0" y="0" width="100%" height="{stats['height']}"
       viewBox="{stats['viewbox']}" xmlns="http://www.w3.org/2000/svg">
    {stats['inner']}
  </svg>
  <svg id="langs-card"
       x="0" y="{langs_y}" width="100%" height="{langs['height']}"
       viewBox="{langs['viewbox']}" xmlns="http://www.w3.org/2000/svg">
    {langs['inner']}
  </svg>
</svg>
{MARKER_END}"""

    with open(README, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END),
        re.DOTALL,
    )
    if MARKER_START not in content:
        print(f"ERROR: markers not found in {README}")
        return

    new_content = pattern.sub(inline_svg, content)

    with open(README, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Updated {README}")


if __name__ == "__main__":
    main()
