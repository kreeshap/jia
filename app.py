import streamlit as st
from PIL import Image
import io
import os
from game2048 import (
    new_board, apply_move, is_won, is_game_over, get_max_tile, TILE_VALUES
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="2048 Face Edition", layout="centered")

st.markdown("""
<style>
  #MainMenu, footer { visibility: hidden; }
  .tile-empty {
    border-radius: 10px; width: 100%; aspect-ratio: 1;
    background: #1e1e1e; display: block;
  }
  .tile-no-photo {
    border-radius: 10px; width: 100%; aspect-ratio: 1;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; font-weight: 800; color: white;
  }
  .tile-value-label {
    text-align: center; font-size: 11px; font-weight: 600;
    color: #aaa; margin-top: 2px; font-family: monospace;
  }
</style>
""", unsafe_allow_html=True)

# ── Load photos from disk (once per session) ──────────────────────────────────
PHOTOS_DIR = os.path.join(os.path.dirname(__file__), "photos")
SUPPORTED_EXTS = [".jpg", ".jpeg", ".png", ".webp"]

@st.cache_resource
def load_photos():
    photos = {}
    for val in TILE_VALUES:
        for ext in SUPPORTED_EXTS:
            path = os.path.join(PHOTOS_DIR, f"{val}{ext}")
            if os.path.exists(path):
                img = Image.open(path).convert("RGB")
                w, h = img.size
                side = min(w, h)
                left = (w - side) // 2
                top = (h - side) // 2
                img = img.crop((left, top, left + side, top + side))
                img = img.resize((200, 200), Image.LANCZOS)
                photos[val] = img
                break
    return photos

PHOTOS = load_photos()

# ── Session state init ────────────────────────────────────────────────────────
def init_state():
    if "board" not in st.session_state:
        st.session_state.board = new_board()
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "best" not in st.session_state:
        st.session_state.best = 0
    if "won" not in st.session_state:
        st.session_state.won = False
    if "over" not in st.session_state:
        st.session_state.over = False
    if "keep_going" not in st.session_state:
        st.session_state.keep_going = False

init_state()

# ── Fallback colors ───────────────────────────────────────────────────────────
TILE_COLORS = {
    2: "#f5e642", 4: "#f5a623", 8: "#f06292", 16: "#e57373",
    32: "#ba68c8", 64: "#7986cb", 128: "#4dd0e1", 256: "#81c784",
    512: "#aed581", 1024: "#4fc3f7", 2048: "#ff8a65",
    4096: "#a1887f", 8192: "#90a4ae", 16384: "#ce93d8", 32768: "#ffffff",
}

# ── Render one tile ───────────────────────────────────────────────────────────
def render_tile(value):
    if value == 0:
        st.markdown('<div class="tile-empty"></div>', unsafe_allow_html=True)
        return
    photo = PHOTOS.get(value)
    if photo:
        buf = io.BytesIO()
        photo.save(buf, format="PNG")
        st.image(buf.getvalue(), use_container_width=True)
        st.markdown(f'<div class="tile-value-label">{value}</div>', unsafe_allow_html=True)
    else:
        color = TILE_COLORS.get(value, "#555")
        st.markdown(
            f'<div class="tile-no-photo" style="background:{color};">{value}</div>',
            unsafe_allow_html=True,
        )

# ── Process a move ────────────────────────────────────────────────────────────
def do_move(direction):
    if st.session_state.over:
        return
    if st.session_state.won and not st.session_state.keep_going:
        return
    board, gained, moved = apply_move(st.session_state.board, direction)
    if moved:
        st.session_state.board = board
        st.session_state.score += gained
        if st.session_state.score > st.session_state.best:
            st.session_state.best = st.session_state.score
        if not st.session_state.won and is_won(board):
            st.session_state.won = True
        if is_game_over(board):
            st.session_state.over = True

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_scores = st.columns([2, 1])
with col_title:
    st.markdown("## 2048 👤 Face Edition")
with col_scores:
    s1, s2 = st.columns(2)
    s1.metric("Score", st.session_state.score)
    s2.metric("Best", st.session_state.best)

# ── Controls ──────────────────────────────────────────────────────────────────
c1, c2, _ = st.columns([1, 1, 2])
with c1:
    if st.button("🔄 New Game", use_container_width=True):
        st.session_state.board = new_board()
        st.session_state.score = 0
        st.session_state.won = False
        st.session_state.over = False
        st.session_state.keep_going = False
        st.rerun()
with c2:
    if st.session_state.won and not st.session_state.keep_going:
        if st.button("Keep going ▶", use_container_width=True):
            st.session_state.keep_going = True
            st.rerun()

# ── Status banners ────────────────────────────────────────────────────────────
if st.session_state.over:
    st.error(f"Game over! Max tile: **{get_max_tile(st.session_state.board)}** — Start a new game.")
elif st.session_state.won and not st.session_state.keep_going:
    st.success("🎉 You reached 2048! Keep going or start a new game.")

# ── Move buttons ──────────────────────────────────────────────────────────────
_, mu, _ = st.columns([1, 1, 1])
with mu:
    if st.button("⬆", use_container_width=True):
        do_move("up"); st.rerun()

ml, mm, mr = st.columns([1, 1, 1])
with ml:
    if st.button("⬅", use_container_width=True):
        do_move("left"); st.rerun()
with mm:
    if st.button("⬇", use_container_width=True):
        do_move("down"); st.rerun()
with mr:
    if st.button("➡", use_container_width=True):
        do_move("right"); st.rerun()

st.markdown("---")

# ── Board ─────────────────────────────────────────────────────────────────────
for row in st.session_state.board:
    cols = st.columns(4, gap="small")
    for col, value in zip(cols, row):
        with col:
            render_tile(value)

# ── Sidebar: verify photo assignments ────────────────────────────────────────
with st.sidebar:
    st.markdown("### Tile assignments")
    if not PHOTOS:
        st.warning("No photos found in `photos/` folder.")
    for val in TILE_VALUES:
        if val in PHOTOS:
            buf = io.BytesIO()
            PHOTOS[val].save(buf, format="PNG")
            st.image(buf.getvalue(), caption=str(val), width=80)
        else:
            color = TILE_COLORS.get(val, "#555")
            st.markdown(
                f'<div style="background:{color};border-radius:6px;width:80px;height:80px;'
                f'display:flex;align-items:center;justify-content:center;'
                f'font-weight:800;color:white;font-size:14px;">{val}</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"{val} — no photo")
