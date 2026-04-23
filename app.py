import streamlit as st
from googleapiclient.discovery import build

API_KEY = st.secrets["API_KEY"]
youtube = build('youtube', 'v3', developerKey=API_KEY)

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

    # 영상 상세정보 (길이 포함)
    video_details = youtube.videos().list(
        part='contentDetails,statistics',
        id=",".join(video_ids)
    ).execute()['items']

    channel_stats = youtube.channels().list(
        part='statistics',
        id=",".join(channel_ids)
    ).execute()['items']

    results = []

    for i in range(len(video_details)):

        duration = video_details[i]['contentDetails']['duration']

        # 👉 쇼츠 제거 (60초 이하 제거)
        if "PT" in duration:
            seconds = 0
            if "M" in duration:
                minutes = int(duration.split("M")[0].replace("PT",""))
                seconds += minutes * 60
            if "S" in duration:
                sec = int(duration.split("S")[0].split("M")[-1])
                seconds += sec

            if seconds <= 60:
                continue

        try:
            views = int(video_details[i]['statistics'].get('viewCount', 0))
        except:
            views = 0

        try:
            subs = int(channel_stats[i]['statistics'].get('subscriberCount', 1))
        except:
            subs = 1

        score = views / subs if subs != 0 else 0

        results.append({
            "title": videos[i]['snippet']['title'],
            "thumbnail": videos[i]['snippet']['thumbnails']['high']['url'],
            "score": round(score, 2)
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:5]


def generate_titles(keyword):
    return [
        f"{keyword} 제대로 하는 방법 (초보 필수)",
        f"{keyword} 모르면 손해 보는 핵심 3가지",
        f"{keyword} 전문가들이 절대 말 안 해주는 이유",
        f"{keyword} 이거 하나로 완전히 달라집니다",
        f"{keyword} 실패하는 사람들의 공통점"
    ]


st.title("유튜브 분석 자동화 툴 (롱폼 전용)")

keyword = st.text_input("키워드 입력")

if st.button("분석 시작"):
    results = analyze(keyword)
    titles = generate_titles(keyword)

    st.subheader("🔥 롱폼 기준 잘 터진 썸네일")
    for r in results:
        st.image(r["thumbnail"])
        st.write(r["title"])
        st.write(f"성과지수: {r['score']}")

    st.subheader("🚀 롱폼 기준 추천 제목")
    for t in titles:
        st.write(t)
