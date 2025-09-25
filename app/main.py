"""Entry point for the file server web application."""
from __future__ import annotations

import datetime
from pathlib import Path
import sys

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from app.auth import login_required  # type: ignore[import-not-found]
    from app.config import DEFAULT_ROOT, SECRET_KEY, UserStore  # type: ignore[import-not-found]
    from app.storage import (  # type: ignore[import-not-found]
        list_directory,
        remove_path,
        resolve_path,
        save_uploaded_file,
    )
else:
    from .auth import login_required
    from .config import DEFAULT_ROOT, SECRET_KEY, UserStore
    from .storage import (
        list_directory,
        remove_path,
        resolve_path,
        save_uploaded_file,
    )

app = Flask(__name__)
app.secret_key = SECRET_KEY

user_store = UserStore()
STORAGE_ROOT = DEFAULT_ROOT
STORAGE_ROOT.mkdir(parents=True, exist_ok=True)


def breadcrumbs(path: Path) -> list[tuple[str, str]]:
    trail = [("Home", url_for("browse"))]
    if path == STORAGE_ROOT:
        return trail
    relative = path.relative_to(STORAGE_ROOT)
    parts = list(relative.parts)
    accum = []
    for part in parts:
        accum.append(part)
        trail.append((part, url_for("browse", path="/".join(accum))))
    return trail


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = user_store.find(username)
        if user and check_password_hash(user.get("password_hash", ""), password):
            session["user"] = username
            flash("Logged in successfully", "success")
            return redirect(request.args.get("next") or url_for("browse"))
        flash("Invalid username or password", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out", "info")
    return redirect(url_for("login"))


@app.route("/", methods=["GET"])
@login_required
def browse():
    requested = request.args.get("path")
    try:
        current_path = resolve_path(STORAGE_ROOT, requested)
    except ValueError:
        abort(400, "Invalid path")

    if current_path.is_file():
        return send_file(current_path, as_attachment=True)

    entries = list_directory(current_path)
    parent = None
    if current_path != STORAGE_ROOT:
        parent = str(current_path.relative_to(STORAGE_ROOT).parent)
    return render_template(
        "browser.html",
        entries=entries,
        breadcrumbs=breadcrumbs(current_path),
        current=current_path,
        parent=parent,
        now=datetime.datetime.utcnow(),
    )


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    requested = request.form.get("path")
    try:
        current_path = resolve_path(STORAGE_ROOT, requested)
    except ValueError:
        abort(400, "Invalid path")
    if "file" not in request.files:
        flash("No file uploaded", "warning")
        return redirect(url_for("browse", path=requested))
    file = request.files["file"]
    try:
        save_uploaded_file(STORAGE_ROOT, current_path, file)
        flash("File uploaded", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("browse", path=requested))


@app.route("/mkdir", methods=["POST"])
@login_required
def make_directory():
    requested = request.form.get("path")
    folder_name = request.form.get("folder-name", "").strip()
    if not folder_name:
        flash("Folder name is required", "warning")
        return redirect(url_for("browse", path=requested))
    try:
        current_path = resolve_path(STORAGE_ROOT, requested)
        new_dir = resolve_path(STORAGE_ROOT, str(current_path.relative_to(STORAGE_ROOT) / folder_name))
        new_dir.mkdir(parents=False, exist_ok=False)
        flash("Folder created", "success")
    except FileExistsError:
        flash("Folder already exists", "warning")
    except ValueError:
        abort(400, "Invalid path")
    return redirect(url_for("browse", path=requested))


@app.route("/delete", methods=["POST"])
@login_required
def delete():
    requested = request.form.get("path")
    target_name = request.form.get("target")
    if not target_name:
        flash("Nothing to delete", "warning")
        return redirect(url_for("browse", path=requested))
    try:
        current_path = resolve_path(STORAGE_ROOT, requested)
        target_path = resolve_path(STORAGE_ROOT, str(current_path.relative_to(STORAGE_ROOT) / target_name))
        if target_path == STORAGE_ROOT:
            flash("Cannot delete storage root", "danger")
        else:
            remove_path(target_path)
            flash("Deleted", "success")
    except ValueError:
        abort(400, "Invalid path")
    return redirect(url_for("browse", path=requested))


@app.context_processor
def inject_user():
    return {
        "current_user": session.get("user"),
        "now": datetime.datetime.utcnow(),
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
