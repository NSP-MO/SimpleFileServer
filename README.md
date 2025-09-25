# Secure Drive File Server

Secure Drive turns a directory on your machine into a password-protected web file server. It is designed to be easy to deploy for personal use while offering essential safeguards such as password hashing, session cookies, and path sanitisation.

## Features

- 🔒 Password-protected access with hashed credentials stored on disk
- 📁 File browser with breadcrumb navigation and folder creation
- 📤 Upload, download, and delete files directly from the web UI
- 🛡️ Storage root isolation to block directory traversal attacks
- ⚙️ Configuration through environment variables for flexible deployment

## Getting started

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure storage and users

The server stores files inside `storage/` by default. You can change the location by setting the `FILESERVER_ROOT` environment variable before launching the app.

Create your first user with the helper script:

```bash
python scripts/create_user.py admin
```

You will be prompted for a password. The credentials are stored in `config/users.json`. The JSON file may be edited manually if required.

> **Tip:** Set `FILESERVER_USERS_FILE` to point at a different credentials file when running multiple instances.

### 3. Run the server

```bash
export FILESERVER_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
flask --app app.main run --host 0.0.0.0 --port 8000
```

Visit `http://localhost:8000` in your browser and log in with the credentials you created.

### 4. Deploying on the internet

When exposing the server publicly, follow these best practices:

- Use HTTPS via a reverse proxy (for example, nginx or Caddy) to protect credentials in transit.
- Choose a strong, unique `FILESERVER_SECRET_KEY` to secure session cookies.
- Create strong passwords for all accounts and rotate them periodically.
- Run the service under a dedicated user account with limited filesystem permissions.
- Enable firewall rules so that only intended clients can reach the server.

## Configuration reference

| Environment variable | Description | Default |
| --- | --- | --- |
| `FILESERVER_ROOT` | Root directory served to clients | `<repo>/storage` |
| `FILESERVER_USERS_FILE` | JSON file storing users and hashed passwords | `<repo>/config/users.json` |
| `FILESERVER_SECRET_KEY` | Secret key for signing Flask session cookies | `change-me` |

## Development

The project uses plain Flask with no database requirements. Templates live under `app/templates` and static assets under `app/static`.

Run the development server with:

```bash
flask --app app.main run --debug
```

Automated tests are not included, but you can run `python -m compileall app` to ensure syntax correctness.
