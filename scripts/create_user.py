"""Utility to create or update a user password for the file server."""
from __future__ import annotations

import argparse
import getpass

from werkzeug.security import generate_password_hash

from app.config import UserStore


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("username", help="Username to create or update")
    parser.add_argument("--password", help="Password (prompted securely if omitted)")
    args = parser.parse_args()

    password = args.password or getpass.getpass(prompt="Password: ")
    if not password:
        raise SystemExit("Password is required")

    store = UserStore()
    store.upsert(args.username, generate_password_hash(password))
    print(f"User '{args.username}' updated.")


if __name__ == "__main__":
    main()
