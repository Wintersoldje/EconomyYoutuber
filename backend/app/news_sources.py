from dataclasses import dataclass
from typing import List, Dict, Tuple
import feedparser
import datetime as dt


@dataclass
class NewsItem:
    source: str
    title: str
    link: str
    published: str
    summary: str


def _today_kst_date_str() -> str:
    # 서버 TZ가 뭐든, 날짜 표기용으로만 사용 (정밀 KST 변환은 추후 확장 가능)
    return dt.datetime.now().strftime("%Y-%m-%d")


def fetch_rss_items(sources: List[Tuple[str, str]], limit: int = 8) -> List[NewsItem]:
    items: List[NewsItem] = []
    for name, url in sources:
        d = feedparser.parse(url)
        for e in (d.entries[:limit] if getattr(d, "entries", None) else []):
            published = getattr(e, "published", "") or getattr(e, "updated", "") or _today_kst_date_str()
            summary = getattr(e, "summary", "") or getattr(e, "description", "") or ""
            items.append(
                NewsItem(
                    source=name,
                    title=getattr(e, "title", "").strip(),
                    link=getattr(e, "link", "").strip(),
                    published=str(published),
                    summary=str(summary),
                )
            )
    # 너무 많으면 상위만
    return items[: limit * max(1, len(sources))]


def fetch_today_news(
    rss_sources: Dict[str, List[Tuple[str, str]]], limit_each: int = 6
) -> Dict[str, List[NewsItem]]:
    return {
        "economy": fetch_rss_items(rss_sources.get("economy", []), limit=limit_each),
        "realestate": fetch_rss_items(rss_sources.get("realestate", []), limit=limit_each),
    }
