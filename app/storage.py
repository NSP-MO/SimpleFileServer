"""Filesystem utilities."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from werkzeug.utils import secure_filename


@dataclass
class Entry:
    name: str
    path: str
    is_dir: bool
    size: int


def resolve_path(root: Path, requested: str | None) -> Path:
    """Resolve a user-supplied path against the storage root safely."""
    if not requested:
        return root
    requested_path = (root / requested).resolve()
    if root not in requested_path.parents and requested_path != root:
        raise ValueError("Invalid path outside storage root")
    return requested_path


def list_directory(path: Path) -> List[Entry]:
    entries: List[Entry] = []
    with os.scandir(path) as it:
        for entry in it:
            if entry.name.startswith('.'):
                continue
            entries.append(
                Entry(
                    name=entry.name,
                    path=str(Path(entry.path).name),
                    is_dir=entry.is_dir(follow_symlinks=False),
                    size=entry.stat(follow_symlinks=False).st_size,
                )
            )
    entries.sort(key=lambda e: (not e.is_dir, e.name.lower()))
    return entries


def save_uploaded_file(root: Path, current: Path, file_storage) -> None:
    filename = secure_filename(file_storage.filename or "")
    if not filename:
        raise ValueError("Empty filename")
    target = resolve_path(root, str(current.relative_to(root) / filename))
    file_storage.save(target)


def remove_path(path: Path) -> None:
    if path.is_dir():
        for child in path.iterdir():
            remove_path(child)
        path.rmdir()
    else:
        path.unlink()
