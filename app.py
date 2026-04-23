import streamlit as st
from googleapiclient.discovery import build
import re
from datetime import datetime

API_KEY = st.secrets["API_KEY"]
youtube = build('youtube', 'v3', developerKey=API_KEY)


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

    # 최근 영상 가중치
    freshness = max(1, 30 / (days + 1))

    # 로그 보정
    import math
    log_views = math.log10(views + 1)

    return base * freshness * log_views


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

        # 롱폼만
        if duration <= 60:
            continue

        try:
            views = int(video_details[i]['statistics'].get('viewCount', 0))
        except:
            views = 0

        if views < 1000:
            continue

        try:
            subs = int(channel_stats[i]['statistics'].get('subscriberCount', 1))
        except:
            subs = 1

        published = video_details[i]['snippet']['publishedAt']
        published_date = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
        days = (datetime.utcnow() - published_date).days

        score = calculate_score(views, subs, days)

        results.append({
            "title": video_details[i]['snippet']['title'],
            "thumbnail": video_details[i]['snippet']['thumbnails']['high']['url'],
            "score": round(score, 2)
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:5]


def generate_titles(keyword):
    return [
        f"{keyword} 이거 모르면 계속 실패합니다",
        f"{keyword} 제대로 하는 방법 (조회수 터지는 구조)",
        f"{keyword} 전문가들이 실제로 쓰는 방법",
        f"{keyword} 이거 하나로 결과가 달라집니다",
        f"{keyword} 대부분이 틀리는 이유"
    ]


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

    # 제목 개선
    improved_titles = [
        title + " (이걸 몰라서 망합니다)",
        title.replace("방법", "진짜 되는 방법"),
        title + " 반드시 알아야 할 핵심",
    ]

    # 썸네일 피드백
    feedback = [
        "텍스트가 작으면 클릭률 떨어집니다",
        "얼굴 클로즈업이 없으면 CTR 낮아질 가능성 있음",
        "대비(빨강/노랑) 부족하면 눈에 안 띔",
        "핵심 키워드 3단어 이내로 줄이기 추천"
    ]

    return title, views, improved_titles, feedback


st.title("유튜브 분석 자동화 툴 (실전 버전)")

# ===== 키워드 분석 =====
keyword = st.text_input("키워드 입력")

if st.button("분석 시작"):
    results = analyze(keyword)
    titles = generate_titles(keyword)

    st.subheader("🔥 성과 좋은 롱폼 영상")
    for r in results:
        st.image(r["thumbnail"])
        st.write(r["title"])
        st.write(f"점수: {r['score']}")

    st.subheader("🚀 추천 제목")
    for t in titles:
        st.write(t)


# ===== 기존 영상 분석 =====
st.subheader("📌 내 영상 개선하기")

video_url = st.text_input("유튜브 영상 링크 입력")

if st.button("영상 분석"):
    result = analyze_existing_video(video_url)

    if result:
        title, views, improved, feedback = result

        st.write("현재 제목:", title)
        st.write("조회수:", views)

        st.subheader("🔥 개선 제목")
        for t in improved:
            st.write(t)

        st.subheader("🎯 썸네일 개선 포인트")
        for f in feedback:
            st.write("-", f)
    else:
        st.write("링크가 올바르지 않습니다")
