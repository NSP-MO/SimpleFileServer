"""Authentication helpers."""
from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import redirect, request, session, url_for

F = TypeVar("F", bound=Callable[..., object])


def login_required(func: F) -> F:
    """View decorator that requires an authenticated user."""

    @wraps(func)
    def wrapper(*args, **kwargs):  # type: ignore[override]
        if not session.get("user"):
            return redirect(url_for("login", next=request.path))
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
