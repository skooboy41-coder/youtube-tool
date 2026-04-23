import streamlit as st
from googleapiclient.discovery import build
import re
from datetime import datetime
import math

st.set_page_config(layout="wide")

API_KEY = st.secrets["API_KEY"]
youtube = build('youtube', 'v3', developerKey=API_KEY)

# =========================
# 스타일
# =========================
st.markdown("""
<style>
.divider {
    width:1px;
    background:#2a2d34;
    height:100%;
}

.card {
    background:#1c1f26;
    padding:15px;
    border-radius:10px;
    margin-bottom:15px;
}

.metric-box {
    background:#2a2d34;
    padding:10px;
    border-radius:8px;
    text-align:center;
}

.metric-title {
    font-size:12px;
    color:#aaa;
}

.metric-value {
    font-size:16px;
    font-weight:bold;
}

.badge-best {color:#ff4d4d; font-weight:bold;}
.badge-good {color:#4dabf7; font-weight:bold;}
.badge-soso {color:#999;}

.video-btn {
    background:#ff0000;
    color:white;
    padding:6px 10px;
    border-radius:6px;
    text-decoration:none;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 유틸
# =========================
def parse_duration(duration):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    h = int(match.group(1)) if match.group(1) else 0
    m = int(match.group(2)) if match.group(2) else 0
    s = int(match.group(3)) if match.group(3) else 0
    return h*3600 + m*60 + s

def calculate_score(views, subs, days):
    if subs == 0:
        subs = 1
    base = views / subs
    freshness = max(1, 30 / (days + 1))
    log_views = math.log10(views + 1)
    return base * freshness * log_views

def score_to_grade(score):
    if score > 8:
        return "🔥 Best"
    elif score > 3:
        return "👍 Good"
    else:
        return "😐 SoSo"

# =========================
# 신규 분석
# =========================
def analyze(query):

    res = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=30
    ).execute()

    videos = res['items']
    video_ids = [v['id']['videoId'] for v in videos]
    channel_ids = [v['snippet']['channelId'] for v in videos]

    video_details = youtube.videos().list(
        part='contentDetails,statistics,snippet',
        id=",".join(video_ids)
    ).execute()['items']

    # 🔥 핵심 수정 (채널 매핑)
    channel_response = youtube.channels().list(
        part='statistics',
        id=",".join(channel_ids)
    ).execute()['items']

    channel_map = {
        c['id']: int(c['statistics'].get('subscriberCount', 1))
        for c in channel_response
    }

    results = []

    for i in range(len(video_details)):

        duration = parse_duration(video_details[i]['contentDetails']['duration'])

        # 롱폼만
        if duration <= 60:
            continue

        try:
            views = int(video_details[i]['statistics'].get('viewCount', 0))
        except:
            views = 0

        channel_id = video_details[i]['snippet']['channelId']
        subs = channel_map.get(channel_id, 1)

        published = video_details[i]['snippet']['publishedAt']
        date = published.split("T")[0]

        published_date = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
        days = (datetime.utcnow() - published_date).days

        score = calculate_score(views, subs, days)

        results.append({
            "title": video_details[i]['snippet']['title'],
            "thumbnail": video_details[i]['snippet']['thumbnails']['high']['url'],
            "views": views,
            "subs": subs,
            "date": date,
            "score": round(score, 2),
            "grade": score_to_grade(score),
            "video_id": video_ids[i]
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:5]

# =========================
# 기존 영상 분석
# =========================
def extract_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1]
    return None

def analyze_existing_video(url):
    vid = extract_video_id(url)
    if not vid:
        return None

    res = youtube.videos().list(
        part='snippet,statistics',
        id=vid
    ).execute()['items'][0]

    title = res['snippet']['title']
    views = int(res['statistics'].get('viewCount', 0))

    improved_titles = [
        title + " (이걸 몰라서 망합니다)",
        title.replace("방법", "진짜 되는 방법"),
        title + " 반드시 알아야 할 핵심",
    ]

    feedback = [
        "텍스트 크게 (3~5단어)",
        "얼굴 클로즈업 추가",
        "강한 색 대비 (빨강/노랑)",
        "핵심 키워드 1개만 강조"
    ]

    return title, views, improved_titles, feedback

# =========================
# UI 구조
# =========================
col1, divider, col2 = st.columns([1, 0.02, 1])

with divider:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# =========================
# 좌측
# =========================
with col1:
    st.header("🔍 신규 영상 분석")

    with st.form("search_form"):
        keyword = st.text_input("키워드 입력")
        submitted = st.form_submit_button("분석 시작")

    if submitted:
        results = analyze(keyword)

        for r in results:
            video_url = f"https://www.youtube.com/watch?v={r['video_id']}"

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.image(r["thumbnail"])

            st.markdown(f"""
            <div style="display:flex; justify-content:space-between;">
            <div><b>{r["title"]}</b></div>
            <a href="{video_url}" target="_blank" class="video-btn">영상 확인</a>
            </div>
            """, unsafe_allow_html=True)

            m1, m2, m3 = st.columns(3)

            with m1:
                st.markdown(f"<div class='metric-box'><div class='metric-title'>조회수</div><div class='metric-value'>{r['views']:,}</div></div>", unsafe_allow_html=True)
            with m2:
                st.markdown(f"<div class='metric-box'><div class='metric-title'>구독자</div><div class='metric-value'>{r['subs']:,}</div></div>", unsafe_allow_html=True)
            with m3:
                st.markdown(f"<div class='metric-box'><div class='metric-title'>업로드</div><div class='metric-value'>{r['date']}</div></div>", unsafe_allow_html=True)

            if "Best" in r["grade"]:
                cls = "badge-best"
            elif "Good" in r["grade"]:
                cls = "badge-good"
            else:
                cls = "badge-soso"

            st.markdown(f"<div class='{cls}'>등급: {r['grade']}</div>", unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 우측
# =========================
with col2:
    st.header("📌 기존 영상 개선")

    with st.form("video_form"):
        url = st.text_input("영상 링크")
        submitted2 = st.form_submit_button("영상 분석")

    if submitted2:
        result = analyze_existing_video(url)

        if result:
            title, views, improved, feedback = result

            st.write("현재 제목:", title)
            st.write("조회수:", f"{views:,}")

            st.subheader("🔥 개선 제목")
            for t in improved:
                st.write("-", t)

            st.subheader("🎯 썸네일 개선")
            for f in feedback:
                st.write("-", f)
