#!/usr/bin/env python3
import argparse
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "memory.db"


def connect():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_state (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    return conn


def set_state(conn, key, value):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO agent_state (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
        """,
        (key, value),
    )
    conn.commit()


def show(conn):
    cur = conn.cursor()
    cur.execute("SELECT key, value, updated_at FROM agent_state ORDER BY updated_at DESC")
    rows = cur.fetchall()
    if not rows:
        print("agent_state vazio")
        return
    for key, value, updated_at in rows:
        print(f"{key}={value} ({updated_at})")


def main():
    parser = argparse.ArgumentParser(description="Controle operacional do Petrovich")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    suspend = sub.add_parser("suspend")
    suspend.add_argument("--reason", default="manual_suspend")
    sub.add_parser("unsuspend")
    args = parser.parse_args()

    conn = connect()
    try:
        if args.cmd == "show":
            show(conn)
        elif args.cmd == "suspend":
            set_state(conn, "posting_suspended", "1")
            set_state(conn, "posting_suspended_reason", args.reason)
            print("posting_suspended=1")
        elif args.cmd == "unsuspend":
            set_state(conn, "posting_suspended", "0")
            set_state(conn, "posting_suspended_reason", "")
            print("posting_suspended=0")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
