"""Entry point for LAN Messenger Server."""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from messenger.shared.constants import DEFAULT_PORT
from messenger.server.server import run_server


def main():
    parser = argparse.ArgumentParser(description="LAN 메신저 서버")
    parser.add_argument(
        "--host", default="0.0.0.0", help="바인딩 주소 (기본: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help=f"포트 번호 (기본: {DEFAULT_PORT})"
    )
    args = parser.parse_args()

    print(f"=== LAN 메신저 서버 ===")
    print(f"주소: {args.host}:{args.port}")
    print(f"서버를 종료하려면 Ctrl+C를 누르세요.")
    print()

    try:
        run_server(args.host, args.port)
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")


if __name__ == "__main__":
    main()
