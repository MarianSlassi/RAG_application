import sys
import sqlite3
import argparse

from src.qabot.repository.log_repository import LogRepository, Database
from src.qabot.helpers.config import Config

def cli_logs():
    parser = argparse.ArgumentParser(description="Fetch logs from SQLite database.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    session_parser = subparsers.add_parser("session", help="Get logs by session id")
    session_parser.add_argument("session_id", help="Session ID to search for")

    range_parser = subparsers.add_parser("range", help="Get logs by time range")
    range_parser.add_argument("start", help="Start timestamp (ISO format)")
    range_parser.add_argument("end", help="End timestamp (ISO format)")

    args = parser.parse_args()
    config = Config()
    repo = LogRepository()

    with Database._connect(config['logs_db']) as conn:
        if args.command == "session":
            for row in repo.get_by_session(args.session_id, conn=conn):
                print(row)
        elif args.command == "range":
            for row in repo.get_by_time_range(args.start, args.end, conn=conn):
                print(row)

if __name__ == '__main__':
    cli_logs()