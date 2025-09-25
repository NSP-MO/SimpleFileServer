"""Configuration helpers for the file server application."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List

DEFAULT_ROOT = Path(os.environ.get("FILESERVER_ROOT", Path.cwd() / "storage")).resolve()
USERS_FILE = Path(os.environ.get("FILESERVER_USERS_FILE", Path.cwd() / "config" / "users.json")).resolve()
SECRET_KEY = os.environ.get("FILESERVER_SECRET_KEY", "change-me")


class UserStore:
    """Simple JSON-backed user store."""

    def __init__(self, path: Path = USERS_FILE) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(json.dumps({"users": []}, indent=2), encoding="utf-8")

    def load(self) -> List[Dict[str, str]]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return data.get("users", [])

    def save(self, users: List[Dict[str, str]]) -> None:
        self.path.write_text(json.dumps({"users": users}, indent=2), encoding="utf-8")

    def find(self, username: str) -> Dict[str, str] | None:
        for user in self.load():
            if user.get("username") == username:
                return user
        return None

    def upsert(self, username: str, password_hash: str) -> None:
        users = self.load()
        for user in users:
            if user.get("username") == username:
                user["password_hash"] = password_hash
                break
        else:
            users.append({"username": username, "password_hash": password_hash})
        self.save(users)
