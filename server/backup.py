import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _run_rcon(command: str) -> str:
    password = os.environ.get("MINECRAFT_RCON_PASSWORD")
    if not password:
        raise RuntimeError("MINECRAFT_RCON_PASSWORD is not set.")

    host = os.environ.get("MINECRAFT_RCON_HOST", "127.0.0.1")
    port = os.environ.get("MINECRAFT_RCON_PORT", "25575")
    default_binary = "/home/ubuntu/mcron/mcrcon-0.7.2-linux-x86-64-static/mcrcon"
    configured_binary = os.environ.get("MINECRAFT_RCON_BINARY", default_binary)

    last_error = "Unknown RCON error."
    for binary in [configured_binary, "mcrcon"]:
        try:
            result = subprocess.run(
                [binary, "-H", host, "-P", port, "-p", password, command],
                capture_output=True,
                text=True,
                timeout=8,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            last_error = str(exc)
            continue

        if result.returncode == 0:
            return result.stdout.strip()

        last_error = result.stderr.strip() or result.stdout.strip() or last_error

    raise RuntimeError(last_error)


def create_world_backup() -> dict:
    server_dir = Path(os.environ.get("MINECRAFT_SERVER_DIR", "/home/ubuntu/mc-1.20.1-forge"))
    world_name = os.environ.get("MINECRAFT_WORLD_NAME", "world")
    backup_dir = Path(os.environ.get("MINECRAFT_BACKUP_DIR", "/home/ubuntu/backup"))

    world_path = server_dir / world_name
    if not world_path.is_dir():
        raise RuntimeError(f"World directory not found: {world_path}")

    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d--%H-%M-%S")
    archive_name = f"backup-{server_dir.name}-{world_name}-{timestamp}.tar.gz"
    archive_path = backup_dir / archive_name

    notes: list[str] = []
    saving_paused = False

    try:
        try:
            _run_rcon("save-off")
            saving_paused = True
            _run_rcon("save-all flush")
        except RuntimeError as exc:
            notes.append(f"RCON quiesce skipped: {exc}")

        result = subprocess.run(
            ["tar", "-czf", str(archive_path), world_name],
            cwd=str(server_dir),
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip() or "tar failed without stderr output"
            raise RuntimeError(stderr)
    finally:
        if saving_paused:
            try:
                _run_rcon("save-on")
            except RuntimeError as exc:
                notes.append(f"Warning: failed to run save-on: {exc}")

    return {
        "ok": True,
        "archive_path": str(archive_path),
        "size_bytes": archive_path.stat().st_size,
        "notes": notes,
    }
