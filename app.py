import streamlit as st
from googleapiclient.discovery import build
import re
from datetime import datetime
import math

st.set_page_config(layout="wide")

API_KEY = st.secrets["API_KEY"]
youtube = build('youtube', 'v3', developerKey=API_KEY)

# =========================
# 유틸
# =========================
def parse_duration(duration):
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    h = int(match.group(1)) if match.group(1) else 0
    m = int(match.group(2)) if match.group(2) else 0
    s = int(match.group(3)) if match.group(3) else 0
    return h*3600 + m*60 + s

def score_to_grade(score):
    if score > 8:
        return "🔥 Best"
    elif score > 3:
        return "👍 Good"
    else:
        return "😐 SoSo"

def calculate_score(views, subs, days):
    if subs == 0:
        subs = 1
    base = views / subs
    freshness = max(1, 30 / (days + 1))
    log_views = math.log10(views + 1)
    return base * freshness * log_views

# =========================
# 신규 영상 분석
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

    channel_stats = youtube.channels().list(
        part='statistics',
        id=",".join(channel_ids)
    ).execute()['items']

    results = []

    for i in range(len(video_details)):
        duration = parse_duration(video_details[i]['contentDetails']['duration'])

        if duration <= 60:
            continue

        try:
            views = int(video_details[i]['statistics'].get('viewCount', 0))
        except:
            views = 0

        try:
            subs = int(channel_stats[i]['statistics'].get('subscriberCount', 1))
        except:
            subs = 1

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
            "grade": score_to_grade(score)
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
        "텍스트 크기 키우기 (3~5단어)",
        "얼굴 or 감정 표현 추가",
        "빨강/노랑 대비 강화",
        "핵심 키워드 1개만 강조"
    ]

    return title, views, improved_titles, feedback

# =========================
# UI
# =========================

st.markdown("""
<style>
body {background-color:#0e1117; color:white;}
.block-container {padding-top:2rem;}
.card {
    background:#1c1f26;
    padding:15px;
    border-radius:10px;
    margin-bottom:15px;
}
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1,1], gap="large")

# =========================
# 좌측 (신규)
# =========================
with col1:
    st.header("🔍 신규 영상 분석")

    keyword = st.text_input("키워드 입력")

    if st.button("분석 시작"):
        results = analyze(keyword)

        for r in results:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.image(r["thumbnail"])
            st.write("제목:", r["title"])
            st.write("조회수:", f"{r['views']:,}")
            st.write("구독자:", f"{r['subs']:,}")
            st.write("업로드:", r["date"])
            st.write("등급:", r["grade"])

            st.markdown('</div>', unsafe_allow_html=True)

# =========================
# 우측 (기존)
# =========================
with col2:
    st.header("📌 기존 영상 개선")

    url = st.text_input("영상 링크")

    if st.button("영상 분석"):
        result = analyze_existing_video(url)

        if result:
            title, views, improved, feedback = result

            st.write("현재 제목:", title)
            st.write("조회수:", views)

            st.subheader("🔥 개선 제목")
            for t in improved:
                st.write("-", t)

            st.subheader("🎯 썸네일 개선")
            for f in feedback:
                st.write("-", f)
