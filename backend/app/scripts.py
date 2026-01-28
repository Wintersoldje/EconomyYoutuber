from typing import Dict, List
from .news_sources import NewsItem
from .config import OPENAI_API_KEY, OPENAI_MODEL
import re


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text).replace("\n", " ").strip()


def _fallback_bullets(items: List[NewsItem], n: int = 5) -> List[str]:
    bullets = []
    for it in items[:n]:
        s = _strip_html(it.summary)[:160]
        if not s:
            s = "핵심 내용 요약이 비어 있어 제목 기반으로 정리합니다."
        bullets.append(f"{it.title} — {s}")
    return bullets


async def _openai_chat(prompt: str) -> str:
    """
    OpenAI SDK를 안 깔아도 돌아가게, requests로 간단 호출 버전.
    (원하면 공식 SDK로 바꿔줄 수 있음)
    """
    import requests
    import json

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "너는 한국어 경제/부동산 뉴스 유튜브 작가다. 과장 없이, 숫자/리스크를 함께 말한다.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
    }
    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    r.raise_for_status()
    data = r.json()
    return data["choices"][0]["message"]["content"].strip()


def _build_prompt(news: Dict[str, List[NewsItem]], mode: str) -> str:
    eco = news.get("economy", [])
    re_ = news.get("realestate", [])

    def pack(items: List[NewsItem]) -> str:
        lines = []
        for it in items[:8]:
            lines.append(
                f"- [{it.source}] {it.title} ({it.published})\n  링크: {it.link}\n  요약: {_strip_html(it.summary)[:240]}"
            )
        return "\n".join(lines)

    if mode == "short":
        return f"""
오늘의 경제/부동산 뉴스를 1분 쇼츠 대본으로 써줘.
- 톤: '돈 벌 기회/리스크를 같이 말하는' 경제 유튜버. 과장 금지.
- 구성: 오프닝 1문장 → 경제 2건 → 부동산 2건 → 오늘의 한 줄 결론(투자 조언이 아니라 관찰/체크포인트).
- 자막용으로 문장을 짧게(한 문장 15~25자 권장).
- 각 뉴스는 '왜 내 돈과 연결되는지'를 1문장 포함.

[경제 뉴스]
{pack(eco)}

[부동산 뉴스]
{pack(re_)}
"""
    else:
        return f"""
오늘의 경제/부동산 뉴스를 5~7분 롱폼 대본으로 써줘.
- 톤: 신뢰형. 숫자/근거/리스크를 함께.
- 구성:
  1) 오프닝(15초)
  2) 경제 이슈 3건(각 60~90초): 배경→핵심→시장에 미치는 경로→체크포인트(지표/일정)
  3) 부동산 이슈 3건(각 60~90초): 정책/금리/수급/심리 관점 포함
  4) 정리: '내일 확인할 것 3가지'로 마무리
- 투자 권유 금지. 대신 체크리스트 중심.
- 문장 중간에 (자막) 표기 말고, 자연스러운 말투로.

[경제 뉴스]
{pack(eco)}

[부동산 뉴스]
{pack(re_)}
"""


async def make_script(news: Dict[str, List[NewsItem]], mode: str) -> str:
    # OpenAI가 있으면 고퀄, 없으면 fallback
    if OPENAI_API_KEY:
        prompt = _build_prompt(news, mode)
        return await _openai_chat(prompt)

    # fallback
    eco_b = _fallback_bullets(news.get("economy", []), n=3)
    re_b = _fallback_bullets(news.get("realestate", []), n=3)
    if mode == "short":
        return (
            "오늘 돈 되는 경제/부동산 뉴스 4개만 1분으로 정리합니다.\n\n"
            "경제:\n- "
            + "\n- ".join(eco_b[:2])
            + "\n\n"
            "부동산:\n- "
            + "\n- ".join(re_b[:2])
            + "\n\n"
            "오늘의 한 줄: 지표/정책 일정 체크하고, 과열이면 리스크부터 봅시다."
        )
    else:
        return (
            "오프닝: 오늘 경제/부동산 흐름을 5~7분으로 정리합니다.\n\n"
            "경제 파트:\n- "
            + "\n- ".join(eco_b)
            + "\n\n"
            "부동산 파트:\n- "
            + "\n- ".join(re_b)
            + "\n\n"
            "마무리: 내일 확인할 것 3가지\n1) 환율/금리\n2) 정책/발표 일정\n3) 거래량/심리 지표"
        )
