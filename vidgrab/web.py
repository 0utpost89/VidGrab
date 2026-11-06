import webbrowser
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from .core import DEFAULT_DIR, FORMATS, QUALITIES, Manager, probe

STATIC = Path(__file__).parent / "static"
app = Flask(__name__, static_folder=str(STATIC))
mgr = Manager()


@app.get("/")
def index():
    return send_from_directory(STATIC, "index.html")


@app.get("/api/config")
def config():
    return jsonify(qualities=QUALITIES, formats=FORMATS, out_dir=str(DEFAULT_DIR))


@app.post("/api/probe")
def api_probe():
    try:
        return jsonify(probe(request.json["url"]))
    except Exception as e:  # noqa: BLE001
        return jsonify(error=str(e)), 400


@app.post("/api/download")
def api_download():
    j = request.json
    job = mgr.add(j["url"], quality=j.get("quality", "best"), fmt=j.get("format", "mp4"),
                  out_dir=j.get("out_dir") or None, playlist=bool(j.get("playlist")),
                  subtitles=bool(j.get("subtitles")))
    return jsonify(job.to_dict())


@app.get("/api/jobs")
def jobs():
    return jsonify([j.to_dict() for j in mgr.jobs.values()])


@app.post("/api/jobs/<jid>/cancel")
def cancel(jid):
    if jid in mgr.jobs:
        mgr.jobs[jid].cancel = True
    return jsonify(ok=True)


def run(host="127.0.0.1", port=8765):
    url = f"http://{host}:{port}"
    print(f"VidGrab running at {url}  (Ctrl+C to quit)")
    try:
        webbrowser.open(url)
    except Exception:  # noqa: BLE001
        pass
    app.run(host=host, port=port, threaded=True)
