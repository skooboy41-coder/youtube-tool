
import streamlit as st
from googleapiclient.discovery import build

API_KEY = st.secrets["API_KEY"]

youtube = build('youtube', 'v3', developerKey=API_KEY)

def search_videos(query):
    res = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=20,
        order="viewCount"
    ).execute()
    return res['items']

def get_video_stats(video_ids):
    res = youtube.videos().list(
        part='statistics',
        id=",".join(video_ids)
    ).execute()
    return res['items']

def get_channel_stats(channel_ids):
    res = youtube.channels().list(
        part='statistics',
        id=",".join(channel_ids)
    ).execute()
    return res['items']

def analyze(query):
    videos = search_videos(query)

    video_ids = [v['id']['videoId'] for v in videos]
    channel_ids = [v['snippet']['channelId'] for v in videos]

    video_stats = get_video_stats(video_ids)
    channel_stats = get_channel_stats(channel_ids)

    results = []

    for i, v in enumerate(videos):
        views = int(video_stats[i]['statistics'].get('viewCount', 0))
        subs = int(channel_stats[i]['statistics'].get('subscriberCount', 1))

        score = views / subs if subs != 0 else 0

        results.append({
            "title": v['snippet']['title'],
            "thumbnail": v['snippet']['thumbnails']['high']['url'],
            "score": round(score, 2)
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:5]

def generate_titles(keyword):
    return [
        f"{keyword} 안 하면 큰일 나는 이유",
        f"{keyword} 90%가 모르는 방법",
        f"{keyword} 전문가만 아는 비밀",
        f"{keyword} 지금 당장 해야 하는 이유",
        f"{keyword} 이거 하나로 끝납니다"
    ]

st.title("유튜브 분석 자동화 툴")

keyword = st.text_input("키워드 입력")

if st.button("분석 시작"):
    results = analyze(keyword)
    titles = generate_titles(keyword)

    st.subheader("썸네일")
    for r in results:
        st.image(r["thumbnail"])
        st.write(r["title"])
        st.write(f"성과지수: {r['score']}")

    st.subheader("추천 제목")
    for t in titles:
        st.write(t)
