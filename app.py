import streamlit as st
import requests
import isodate

API_KEY = st.secrets["API_KEY"]

st.set_page_config(layout="wide")

# =========================
# 🎨 스타일 (완전 안정 버전)
# =========================
st.markdown("""
<style>
body {
    background-color: #0b0f17;
    color: white;
}

.block-container {
    padding: 20px 40px;
}

.divider {
    border-left: 1px solid #222;
    height: 100%;
}

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

.badge-best {color:#ff4d4d;font-weight:bold;}
.badge-good {color:#4dabf7;}
.badge-so {color:#888;}

.btn {
    background: #ff0000;
    padding: 6px 10px;
    border-radius: 6px;
    color: white;
    text-decoration: none;
    font-size: 12px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🔧 함수
# =========================
def search_videos(keyword):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=20&q={keyword}&key={API_KEY}"
    return requests.get(url).json()["items"]

def get_video_stats(ids):
    url = f"https://www.googleapis.com/youtube/v3/videos?part=statistics,contentDetails&id={','.join(ids)}&key={API_KEY}"
    return requests.get(url).json()["items"]

def get_channel_stats(ids):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={','.join(ids)}&key={API_KEY}"
    return requests.get(url).json()["items"]

def parse_duration(d):
    try:
        sec = int(isodate.parse_duration(d).total_seconds())
        return sec
    except:
        return 0

def analyze(keyword):
    videos = search_videos(keyword)

    video_ids = [v["id"]["videoId"] for v in videos]
    channel_ids = [v["snippet"]["channelId"] for v in videos]

    stats = get_video_stats(video_ids)
    channels = get_channel_stats(channel_ids)

    results = []

    for i, v in enumerate(videos):
        try:
            duration = parse_duration(stats[i]["contentDetails"]["duration"])
            if duration < 60:
                continue  # 쇼츠 제외

            views = int(stats[i]["statistics"].get("viewCount", 0))
            subs = int(channels[i]["statistics"].get("subscriberCount", 1))

            score = views / subs if subs > 0 else views

            if score > 5:
                grade = "🔥 Best"
                cls = "badge-best"
            elif score > 2:
                grade = "Good"
                cls = "badge-good"
            else:
                grade = "So So"
                cls = "badge-so"

            results.append({
                "title": v["snippet"]["title"],
                "thumb": v["snippet"]["thumbnails"]["medium"]["url"],
                "views": views,
                "subs": subs,
                "date": v["snippet"]["publishedAt"][:10],
                "video_id": v["id"]["videoId"],
                "grade": grade,
                "cls": cls
            })
        except:
            continue

    return sorted(results, key=lambda x: x["views"], reverse=True)

# =========================
# 🎯 UI
# =========================
st.title("유튜브 분석 자동화 툴 (실전 버전)")

col1, col_mid, col2 = st.columns([1, 0.02, 1])

# =========================
# 왼쪽 (신규 분석)
# =========================
with col1:
    keyword = st.text_input("키워드 입력")

    if keyword:
        if st.button("분석 시작") or st.session_state.get("enter"):
            results = analyze(keyword)

            for r in results:
                video_url = f"https://youtube.com/watch?v={r['video_id']}"

                st.markdown(f"""
                <div class="card">
                    <img class="thumb" src="{r['thumb']}">
                    
                    <div>
                        <div class="title">{r['title']}</div>
                        <div class="meta">업로드: {r['date']}</div>
                    </div>

                    <div>{r['views']:,}</div>
                    <div>{r['subs']:,}</div>
                    <div class="{r['cls']}">{r['grade']}</div>

                    <div>
                        <a class="btn" href="{video_url}" target="_blank">영상 보기</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# =========================
# 가운데 선
# =========================
with col_mid:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# =========================
# 오른쪽 (영상 개선)
# =========================
with col2:
    st.subheader("내 영상 개선")

    url = st.text_input("유튜브 링크")

    if st.button("영상 분석"):
        st.write("제목 개선:")
        st.write("이 제목은 클릭 유도가 약합니다 → 숫자 + 결과 강조 필요")

        st.write("썸네일 개선:")
        st.write("얼굴 클로즈업 + 대비 색상 부족")
