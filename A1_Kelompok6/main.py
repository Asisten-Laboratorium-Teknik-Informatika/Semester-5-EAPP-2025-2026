"""Entry point aplikasi AttendanceHub berbasis Eel."""

from __future__ import annotations

import argparse
import os

import eel  # type: ignore

from logic import attendance, auth, face_detection  # noqa: F401 (import side-effects for eel)
from logic.database import init_database


def parse_args():
    parser = argparse.ArgumentParser(description="AttendanceHub Desktop App")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=8085)
    parser.add_argument("--mode", default="chrome-app", help="Mode Eel (chrome-app / default / none)")
    parser.add_argument("--start-page", default="login.html")
    parser.add_argument("--size", type=int, nargs=2, default=[1280, 720])
    return parser.parse_args()


def main():
    args = parse_args()
    init_database()

    web_dir = os.path.join(os.path.dirname(__file__), "web")
    eel.init(web_dir)

    width, height = args.size
    eel.start(
        args.start_page,
        size=(width, height),
        host=args.host,
        port=args.port,
        mode=args.mode,
        block=True,
    )


if __name__ == "__main__":
    main()

