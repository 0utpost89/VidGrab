# VidGrab

A free, open-source video downloader with a clean local web UI and a CLI. Built on
[yt-dlp](https://github.com/yt-dlp/yt-dlp) and FFmpeg, so it supports the same
~1,000+ sites yt-dlp does. No accounts, no licenses, no limits.

## Features
- Paste a URL → pick format (MP4/MKV/WebM or MP3/M4A/Opus) and quality (up to 4K+)
- Playlist and channel downloads
- Subtitle download
- Live progress, speed, ETA, cancel
- Runs locally — nothing leaves your machine

## Install
Requires Python 3.9+ and [FFmpeg](https://ffmpeg.org/download.html) on your PATH.

```bash
git clone https://github.com/<you>/VidGrab && cd VidGrab
pip install .
```

## Use
```bash
vidgrab web                       # open the UI at http://127.0.0.1:8765
vidgrab get URL -q 1080 -f mp4    # CLI download
vidgrab get PLAYLIST_URL --playlist -f mp3
```
Files save to `~/Downloads/VidGrab` (override with `VIDGRAB_DIR` or `-o`).

Keep it working by updating the engine now and then: `pip install -U yt-dlp`.

## Legal
VidGrab is intended for downloading content you have the right to save (your own
uploads, Creative Commons / public-domain media, or personal copies where permitted
in your country). It does not circumvent DRM, and you're responsible for following the
terms of the sites you use and applicable copyright law.

## License
MIT
