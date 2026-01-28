import os
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
FFMPEG_BIN = os.getenv("FFMPEG_BIN", "ffmpeg").strip()

# 기본 RSS 소스(예시). 필요하면 네가 원하는 매체로 교체 가능
RSS_SOURCES = {
    "economy": [
        ("연합뉴스 경제", "https://www.yna.co.kr/rss/economy.xml"),
        ("매일경제 경제", "https://www.mk.co.kr/rss/30000001/"),
    ],
    "realestate": [
        ("연합뉴스 부동산/건설", "https://www.yna.co.kr/rss/realestate.xml"),
        ("국토교통부 보도자료", "https://www.molit.go.kr/rss/rss.xml"),
    ],
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)
