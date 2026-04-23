import streamlit as st
import requests
import isodate

API_KEY = st.secrets["API_KEY"]

st.set_page_config(layout="wide")

# =========================
# 🎨 스타일 (다크 + 고급 UI)
# =========================
st.markdown("""
<style>

body {
    background: #0b0f17;
    color: white;
}

.block-container {
    padding: 20px 40px;
}

h1 {
    font-size: 32px;
    font-weight: 700;
}

/* 좌우 레이아웃 */
.split {
    display: flex;
    gap: 30px;
}

.left, .right {
    width: 50%;
}

/* 세로 구분선 */
.divider {
    width: 1px;
    background: #222;
}

/* 입력창 */
.stTextInput > div > div > input {
    background: #111827;
    color: white;
    border: 1px solid #333;
}

/* 버튼 */
.stButton button {
    background: linear-gradient(90deg, #4dabf7, #339af0);
    border: none;
    color: white;
    font-weight: bold;
    border-radius: 8px;
}

/* 결과 카드 */
.card {
    display: grid;
    grid-template-columns: 140px 1fr 120px 120px 120px 120px;
    align-items: center;
    padding: 12px;
    border-bottom: 1px solid #1f2937;
}

.card:hover {
    background: #111827;
}

.thumb {
    width: 120px;
    border-radius: 10px;
}

.title {
    font-size: 14px;
    font-weight: 600;
}

.meta {
    font-size: 12px;
    color: #aaa;
}

.badge-best {
    color: #ff4d4d;
    font-weight: bold;
}

.badge-good {
    color: #4dabf7;
}

.badge-so {
    color: #888;
}

.btn {
    background: #ff0000;
    padding: 6px 10px;
    border-radius: 6px;
    color: white;
    text-decoration: none;
    font-size: 12px;
}

</style>
""", unsafe
