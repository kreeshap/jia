from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="2048 Face Edition", page_icon="🧩", layout="centered")

st.markdown(
    """
<style>
/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
header { visibility: hidden; }
footer { visibility: hidden; }

/* Tighten spacing so the embed matches the standalone HTML more closely */
div.block-container { padding-top: 1rem; padding-bottom: 1rem; }
</style>
""",
    unsafe_allow_html=True,
)

HTML_PATH = Path(__file__).with_name("2048_face_edition_enhanced.html")
PHOTOS_DIR = Path(__file__).with_name("photos")

raw_html = HTML_PATH.read_text(encoding="utf-8", errors="replace")

TILE_VALUES = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192]


def _guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def _to_data_uri(path: Path) -> str:
    mime = _guess_mime(path)
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def load_default_photos(photos_dir: Path) -> dict[int, str]:
    if not photos_dir.exists():
        return {}

    photos: dict[int, str] = {}
    for value in TILE_VALUES:
        matches = sorted(
            [p for p in photos_dir.glob(f"{value}.*") if p.is_file()],
            key=lambda p: p.suffix.lower(),
        )
        if not matches:
            continue
        photos[value] = _to_data_uri(matches[0])

    return photos


default_photos = load_default_photos(PHOTOS_DIR)
if default_photos:
    injected = json.dumps({str(k): v for k, v in default_photos.items()})
    # The HTML declares `let photos = {};` and then optionally overwrites from localStorage.
    # We pre-seed `photos` so the game starts with your face tiles immediately.
    raw_html = raw_html.replace("let photos = {};", f"let photos = {injected};")

css_vars = """
<style>
:root{
  --font-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, "Apple Color Emoji",
    "Segoe UI Emoji";
  --color-text-primary: #eaeaea;
  --color-text-secondary: #a9a9b2;
  --color-background-secondary: #242428;
  --color-background-info: #3b82f6;
  --color-text-info: #ffffff;
  --color-background-success: #22c55e;
  --color-text-success: #06220f;
  --color-background-danger: #ef4444;
  --color-text-danger: #ffffff;
  --color-border-tertiary: rgba(255,255,255,0.22);
  --color-border-secondary: rgba(255,255,255,0.32);
  --color-border-primary: rgba(255,255,255,0.55);
  --border-radius-md: 12px;
  --border-radius-lg: 16px;
}

html, body {
  margin: 0;
  padding: 0;
  background: #0f0f10;
}
</style>
"""

full_html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    {css_vars}
  </head>
  <body>
    {raw_html}
  </body>
</html>
"""

components.html(full_html, height=1000, scrolling=True)
