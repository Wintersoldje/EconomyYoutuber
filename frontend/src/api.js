export async function fetchScript(mode) {
  const r = await fetch(`/api/script/${mode}`, { method: "POST" });
  if (!r.ok) throw new Error(await r.text());
  return await r.json(); // {script}
}

export async function makeVideo(mode, script) {
  const r = await fetch(`/api/video/${mode}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ script })
  });
  if (!r.ok) throw new Error(await r.text());
  return await r.json(); // {filename}
}

export function downloadUrl(filename) {
  return `/api/download/${encodeURIComponent(filename)}`;
}
