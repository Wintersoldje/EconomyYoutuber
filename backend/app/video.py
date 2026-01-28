import os
import subprocess
import textwrap
import uuid
from typing import List, Optional
import requests

from .config import OUTPUT_DIR, FFMPEG_BIN, UNSPLASH_ACCESS_KEY


def _run(cmd: List[str]) -> None:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{p.stderr}")


def _safe_filename(name: str) -> str:
    keep = "".join(c for c in name if c.isalnum() or c in ("-", "_"))
    return keep[:64] or "file"


def _make_srt(lines: List[str], seconds_per_line: float) -> str:
    # 매우 단순 SRT 생성(후에 길이/타이밍 개선 가능)
    def ts(t: float) -> str:
        h = int(t // 3600)
        m = int((t % 3600) // 60)
        s = int(t % 60)
        ms = int((t - int(t)) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    out = []
    t = 0.0
    for i, line in enumerate(lines, 1):
        start = t
        end = t + seconds_per_line
        t = end
        out.append(str(i))
        out.append(f"{ts(start)} --> {ts(end)}")
        out.append(line.strip())
        out.append("")
    return "\n".join(out).strip() + "\n"


def _split_for_subtitles(script: str) -> List[str]:
    # 자막은 짧게: 문장 기준 대충 쪼개기
    raw = []
    for part in script.replace("\r", "\n").split("\n"):
        part = part.strip()
        if not part:
            continue
        raw.extend([s.strip() for s in part.split(".") if s.strip()])
    # 너무 길면 줄바꿈
    lines = []
    for s in raw:
        s = s.replace("—", "-")
        chunks = textwrap.wrap(s, width=22)
        for c in chunks[:2]:  # 한 문장 너무 길면 잘라서 2줄까지만
            lines.append(c)
    return lines[:60]  # 제한


def _download_unsplash(keyword: str, out_path: str) -> bool:
    if not UNSPLASH_ACCESS_KEY:
        return False
    url = "https://api.unsplash.com/photos/random"
    params = {"query": keyword, "orientation": "landscape", "content_filter": "high"}
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    r = requests.get(url, params=params, headers=headers, timeout=30)
    if r.status_code != 200:
        return False
    data = r.json()
    img_url = data.get("urls", {}).get("regular")
    if not img_url:
        return False
    img = requests.get(img_url, timeout=60)
    if img.status_code != 200:
        return False
    with open(out_path, "wb") as f:
        f.write(img.content)
    return True


def _make_text_card(text: str, out_png: str) -> None:
    """
    외부 라이브러리 없이 ffmpeg drawtext로 '텍스트 카드' PNG 생성.
    (폰트는 시스템 기본을 사용. 폰트 이슈 생기면 assets/font.ttf 넣고 지정 가능)
    """
    # 배경 단색 + 큰 제목 텍스트
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=black:s=1280x720:d=1",
        "-vf",
        f"drawtext=text='{text.replace(':','\\:').replace("'", "\\'")}':"
        "fontcolor=white:fontsize=54:x=(w-text_w)/2:y=(h-text_h)/2",
        "-frames:v",
        "1",
        out_png,
    ]
    _run(cmd)


def render_video_from_script(
    script: str,
    mode: str,
    voice_mp3: Optional[str] = None,
) -> str:
    """
    MVP: 이미지 1장(키워드 기반) + 자막 번인 + 오디오(없으면 무음) 로 mp4 생성
    확장: 뉴스별 여러 이미지 슬라이드/씬 구성 가능
    """
    uid = uuid.uuid4().hex[:10]
    base = os.path.join(OUTPUT_DIR, f"{mode}_{uid}")
    os.makedirs(base, exist_ok=True)

    # 1) 대표 이미지 준비 (Unsplash 있으면 키워드로, 없으면 텍스트 카드)
    img_path = os.path.join(base, "cover.jpg")
    ok = _download_unsplash("economy,real estate,korea", img_path)
    if not ok:
        # jpg 대신 png 만들고, jpg로 변환
        card_png = os.path.join(base, "card.png")
        _make_text_card("TODAY MONEY NEWS", card_png)
        _run([FFMPEG_BIN, "-y", "-i", card_png, "-q:v", "2", img_path])

    # 2) 자막(srt)
    lines = _split_for_subtitles(script)
    total_sec = 60 if mode == "short" else 390  # 6분 30초 기본(5~7분 범위)
    seconds_per_line = max(1.6, total_sec / max(1, len(lines)))
    srt = _make_srt(lines, seconds_per_line)
    srt_path = os.path.join(base, "sub.srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt)

    # 3) 오디오: MVP는 무음 (추후 TTS 붙이기)
    audio_path = voice_mp3 or os.path.join(base, "silent.mp3")
    if not voice_mp3:
        _run(
            [
                FFMPEG_BIN,
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=44100:cl=stereo",
                "-t",
                str(total_sec),
                audio_path,
            ]
        )

    # 4) 영상: 커버 1장 반복 + 자막 번인
    out_mp4 = os.path.join(OUTPUT_DIR, f"{mode}_final_{uid}.mp4")
    vf = f"subtitles={srt_path}"
    cmd = [
        FFMPEG_BIN,
        "-y",
        "-loop",
        "1",
        "-i",
        img_path,
        "-i",
        audio_path,
        "-t",
        str(total_sec),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        out_mp4,
    ]
    _run(cmd)
    return out_mp4
