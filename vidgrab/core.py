"""Download engine: a thin, friendly layer over yt-dlp."""
import os
import threading
import uuid
from pathlib import Path

import yt_dlp

DEFAULT_DIR = Path(os.environ.get("VIDGRAB_DIR", Path.home() / "Downloads" / "VidGrab"))

QUALITIES = ["best", "2160", "1440", "1080", "720", "480", "360"]
FORMATS = ["mp4", "mkv", "webm", "mp3", "m4a", "opus"]
AUDIO_FORMATS = {"mp3", "m4a", "opus"}


def build_opts(quality="best", fmt="mp4", out_dir=None, playlist=False,
               subtitles=False, hook=None):
    out_dir = Path(out_dir or DEFAULT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    tmpl = "%(playlist_title|)s/%(title).150B [%(id)s].%(ext)s" if playlist \
        else "%(title).150B [%(id)s].%(ext)s"
    opts = {
        "outtmpl": str(out_dir / tmpl),
        "noplaylist": not playlist,
        "quiet": True,
        "no_warnings": True,
        "progress_hooks": [hook] if hook else [],
        "restrictfilenames": False,
        "windowsfilenames": True,
    }
    if fmt in AUDIO_FORMATS:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": fmt,
                                   "preferredquality": "0"}]
    else:
        h = "" if quality == "best" else f"[height<={int(quality)}]"
        opts["format"] = f"bv*{h}+ba/b{h}"
        opts["merge_output_format"] = fmt
    if subtitles:
        opts.update(writesubtitles=True, writeautomaticsub=True,
                    subtitleslangs=["en.*"])
    return opts


def probe(url):
    """Return metadata for a URL without downloading."""
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True,
                           "extract_flat": "in_playlist", "skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    entries = info.get("entries")
    return {
        "title": info.get("title"),
        "uploader": info.get("uploader") or info.get("channel"),
        "duration": info.get("duration"),
        "thumbnail": info.get("thumbnail"),
        "is_playlist": entries is not None,
        "count": len(list(entries)) if entries is not None else 1,
    }


class Job:
    def __init__(self, url, **kw):
        self.id = uuid.uuid4().hex[:8]
        self.url = url
        self.kw = kw
        self.status = "queued"
        self.percent = 0.0
        self.speed = ""
        self.eta = ""
        self.title = url
        self.error = None
        self.cancel = False

    def hook(self, d):
        if self.cancel:
            raise yt_dlp.utils.DownloadCancelled("cancelled")
        info = d.get("info_dict") or {}
        self.title = info.get("title", self.title)
        if d["status"] == "downloading":
            self.status = "downloading"
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            if total:
                self.percent = round(d.get("downloaded_bytes", 0) / total * 100, 1)
            self.speed = (d.get("_speed_str") or "").strip()
            self.eta = (d.get("_eta_str") or "").strip()
        elif d["status"] == "finished":
            self.status = "processing"
            self.percent = 100.0

    def run(self):
        try:
            self.status = "downloading"
            with yt_dlp.YoutubeDL(build_opts(hook=self.hook, **self.kw)) as ydl:
                ydl.download([self.url])
            self.status = "done"
        except yt_dlp.utils.DownloadCancelled:
            self.status = "cancelled"
        except Exception as e:  # noqa: BLE001
            self.status, self.error = "error", str(e)

    def to_dict(self):
        return {k: getattr(self, k) for k in
                ("id", "url", "title", "status", "percent", "speed", "eta", "error")}


class Manager:
    def __init__(self):
        self.jobs = {}

    def add(self, url, **kw):
        job = Job(url, **kw)
        self.jobs[job.id] = job
        threading.Thread(target=job.run, daemon=True).start()
        return job
