import React, { useMemo, useState } from "react";
import { fetchScript, makeVideo, downloadUrl } from "./api";
import "./styles.css";

function saveText(filename, text) {
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

export default function App() {
  const [shortScript, setShortScript] = useState("");
  const [longScript, setLongScript] = useState("");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  const today = useMemo(() => {
    const d = new Date();
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  }, []);

  async function onShortScript() {
    setBusy(true);
    setStatus("숏폼 대본 생성 중… (RSS 수집 → 요약)");
    try {
      const { script } = await fetchScript("short");
      setShortScript(script);
      saveText(`${today}_short_script.txt`, script);
      setStatus("완료: 숏폼 대본 생성 + 다운로드");
    } catch (e) {
      setStatus(`에러:\n${e.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function onLongScript() {
    setBusy(true);
    setStatus("롱폼 대본 생성 중… (RSS 수집 → 구성 확장)");
    try {
      const { script } = await fetchScript("long");
      setLongScript(script);
      saveText(`${today}_long_script.txt`, script);
      setStatus("완료: 롱폼 대본 생성 + 다운로드");
    } catch (e) {
      setStatus(`에러:\n${e.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function onShortVideo() {
    setBusy(true);
    setStatus("숏폼 영상 렌더링 중… (이미지 → 자막 → ffmpeg 합성)");
    try {
      const script = shortScript || "(대본이 비어있습니다) 먼저 숏폼 대본을 생성하세요.";
      const { filename } = await makeVideo("short", script);
      const a = document.createElement("a");
      a.href = downloadUrl(filename);
      a.download = filename;
      a.click();
      setStatus(`완료: 숏폼 영상 생성\n${filename}`);
    } catch (e) {
      setStatus(`에러:\n${e.message}`);
    } finally {
      setBusy(false);
    }
  }

  async function onLongVideo() {
    setBusy(true);
    setStatus("롱폼 영상 렌더링 중… (이미지 → 자막 → ffmpeg 합성)");
    try {
      const script = longScript || "(대본이 비어있습니다) 먼저 롱폼 대본을 생성하세요.";
      const { filename } = await makeVideo("long", script);
      const a = document.createElement("a");
      a.href = downloadUrl(filename);
      a.download = filename;
      a.click();
      setStatus(`완료: 롱폼 영상 생성\n${filename}`);
    } catch (e) {
      setStatus(`에러:\n${e.message}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="container">
      <div className="card">
        <h1>경제/부동산 뉴스 영상 제작기</h1>
        <p className="sub">
          컨셉: “돈 되는 뉴스만” 요약하는 경제 유튜버. (과장 금지, 리스크 포함) <br />
          버튼 4개: 숏폼 대본 / 롱폼 대본 / 숏폼 영상 / 롱폼 영상
        </p>

        <div className="row">
          <div>
            <h1 style={{ fontSize: 16, marginTop: 0 }}>숏폼 대본</h1>
            <textarea
              value={shortScript}
              onChange={(e) => setShortScript(e.target.value)}
              placeholder="숏폼 대본이 여기에 표시됩니다."
            />
            <div className="btns">
              <button onClick={onShortScript} disabled={busy}>
                숏폼 대본
              </button>
              <button onClick={onShortVideo} disabled={busy} className="secondary">
                숏폼 영상 만들기
              </button>
            </div>
          </div>

          <div>
            <h1 style={{ fontSize: 16, marginTop: 0 }}>롱폼 대본</h1>
            <textarea
              value={longScript}
              onChange={(e) => setLongScript(e.target.value)}
              placeholder="롱폼 대본이 여기에 표시됩니다."
            />
            <div className="btns">
              <button onClick={onLongScript} disabled={busy}>
                롱폼 대본
              </button>
              <button onClick={onLongVideo} disabled={busy} className="secondary">
                롱폼 영상 만들기
              </button>
            </div>
          </div>
        </div>

        <div className="status">{status}</div>
      </div>
    </div>
  );
}
