import argparse
import sys

from .core import DEFAULT_DIR, FORMATS, QUALITIES, build_opts
import yt_dlp


def main(argv=None):
    p = argparse.ArgumentParser(prog="vidgrab", description="VidGrab - free video downloader")
    sub = p.add_subparsers(dest="cmd")

    d = sub.add_parser("get", help="download one or more URLs")
    d.add_argument("urls", nargs="+")
    d.add_argument("-q", "--quality", choices=QUALITIES, default="best")
    d.add_argument("-f", "--format", choices=FORMATS, default="mp4")
    d.add_argument("-o", "--out", default=str(DEFAULT_DIR))
    d.add_argument("--playlist", action="store_true", help="download whole playlist")
    d.add_argument("--subs", action="store_true", help="download subtitles")

    w = sub.add_parser("web", help="start the local web UI")
    w.add_argument("--host", default="127.0.0.1")
    w.add_argument("--port", type=int, default=8765)

    a = p.parse_args(argv)
    if a.cmd == "get":
        opts = build_opts(a.quality, a.format, a.out, a.playlist, a.subs)
        opts["quiet"] = False
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.download(a.urls)
    if a.cmd == "web":
        from .web import run
        run(a.host, a.port)
        return 0
    p.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
