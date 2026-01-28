from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel

from .config import RSS_SOURCES, OUTPUT_DIR
from .news_sources import fetch_today_news
from .scripts import make_script
from .video import render_video_from_script
import os

app = FastAPI(title="News Video Maker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 배포 시 도메인 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ScriptResp(BaseModel):
    script: str


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/script/{mode}", response_model=ScriptResp)
async def api_make_script(mode: str):
    if mode not in ("short", "long"):
        return PlainTextResponse("mode must be short or long", status_code=400)

    news = fetch_today_news(RSS_SOURCES, limit_each=6)
    script = await make_script(news, mode=mode)
    return {"script": script}


class VideoReq(BaseModel):
    script: str


@app.post("/api/video/{mode}")
async def api_make_video(mode: str, req: VideoReq):
    if mode not in ("short", "long"):
        return PlainTextResponse("mode must be short or long", status_code=400)

    out_mp4 = render_video_from_script(req.script, mode=mode)
    return {"filename": os.path.basename(out_mp4)}


@app.get("/api/download/{filename}")
def download(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(path):
        return PlainTextResponse("file not found", status_code=404)
    return FileResponse(path, media_type="video/mp4", filename=filename)
