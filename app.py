from __future__ import annotations

import base64
import json
import mimetypes
from io import BytesIO
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


def _read_as_web_image(path: Path) -> tuple[bytes, str]:
    suffix = path.suffix.lower()
    if suffix in {".heic", ".heif"}:
        try:
            from PIL import Image
        except Exception as e:  # pragma: no cover
            raise RuntimeError("Pillow is required to convert HEIC/HEIF images.") from e

        try:
            import pillow_heif

            pillow_heif.register_heif_opener()
        except Exception as e:  # pragma: no cover
            raise RuntimeError("pillow-heif is required to convert HEIC/HEIF images.") from e

        img = Image.open(path)
        buf = BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=92, optimize=True)
        return buf.getvalue(), "image/jpeg"

    mime = _guess_mime(path)
    return path.read_bytes(), mime


def _to_data_uri(path: Path) -> str:
    data_bytes, mime = _read_as_web_image(path)
    data = base64.b64encode(data_bytes).decode("ascii")
    return f"data:{mime};base64,{data}"


def load_default_photos(photos_dir: Path) -> dict[int, str]:
    if not photos_dir.exists():
        return {}

    preferred_ext_order = [
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".gif",
        ".heic",
        ".heif",
    ]
    ext_rank = {ext: i for i, ext in enumerate(preferred_ext_order)}

    photos: dict[int, str] = {}
    for value in TILE_VALUES:
        matches = [p for p in photos_dir.glob(f"{value}.*") if p.is_file()]
        matches.sort(key=lambda p: ext_rank.get(p.suffix.lower(), 999))
        if not matches:
            continue

        # Try preferred formats first; if HEIC conversion isn't available, fall back to jpg/png if present.
        for candidate in matches:
            try:
                photos[value] = _to_data_uri(candidate)
                break
            except Exception:
                continue

    return photos


default_photos = load_default_photos(PHOTOS_DIR)
if default_photos:
    injected = json.dumps({str(k): v for k, v in default_photos.items()})
    # The HTML declares `let photos = {};` and then optionally overwrites from localStorage.
    # We pre-seed `photos` so the game starts with your face tiles immediately.
    raw_html = raw_html.replace("let photos = {};", f"let photos = {injected};")

# Prevent uploading HEIC/HEIF (browsers typically can't render them in <img> reliably)
raw_html = raw_html.replace("input.accept = 'image/*';", "input.accept = 'image/png,image/jpeg,image/webp';")

# When loading saved photos, ignore HEIC/HEIF data URIs (they render as broken images).
_merge_saved_photos_js = """
{
  const parsed = JSON.parse(savedPhotos || "{}") || {};
  for (const [k, v] of Object.entries(parsed)) {
    if (typeof v === "string" && (v.startsWith("data:image/heic") || v.startsWith("data:image/heif"))) {
      continue;
    }
    photos[k] = v;
  }
  // Rewrite storage without HEIC/HEIF so it doesn't keep breaking next load.
  try { localStorage.setItem('2048-photos', JSON.stringify(photos)); } catch (e) {}
}
""".strip()

raw_html = raw_html.replace("photos = JSON.parse(savedPhotos);", _merge_saved_photos_js)
raw_html = raw_html.replace("Object.assign(photos, JSON.parse(savedPhotos));", _merge_saved_photos_js)

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
