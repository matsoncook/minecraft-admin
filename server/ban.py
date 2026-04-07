import os
import re
import subprocess
from typing import Callable

VALID_PLAYER_NAME = re.compile(r"^[A-Za-z0-9_]{1,16}$")


def ban_server_player(
    run_cmd: Callable[[list[str]], str],
    service_name: str,
    player_name: str,
    reason: str | None = None,
) -> dict:
    _ = (run_cmd, service_name)

    if not VALID_PLAYER_NAME.fullmatch(player_name):
        raise ValueError("Invalid player name. Use 1-16 chars: letters, numbers, underscore.")

    password = os.environ.get("MINECRAFT_RCON_PASSWORD")
    if not password:
        raise RuntimeError("MINECRAFT_RCON_PASSWORD is not set.")

    host = os.environ.get("MINECRAFT_RCON_HOST", "127.0.0.1")
    port = os.environ.get("MINECRAFT_RCON_PORT", "25575")
    default_binary = "/home/ubuntu/mcron/mcrcon-0.7.2-linux-x86-64-static/mcrcon"
    configured_binary = os.environ.get("MINECRAFT_RCON_BINARY", default_binary)

    ban_reason = (reason or "Banned by admin").strip()
    command = f"ban {player_name} {ban_reason}"

    last_error = "Unknown RCON error."
    for binary in [configured_binary, "mcrcon"]:
        try:
            result = subprocess.run(
                [binary, "-H", host, "-P", port, "-p", password, command],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
            last_error = str(exc)
            continue

        if result.returncode == 0:
            return {
                "ok": True,
                "player": player_name,
                "reason": ban_reason,
                "output": result.stdout.strip(),
            }

        last_error = result.stderr.strip() or result.stdout.strip() or last_error

    raise RuntimeError(f"Failed to ban player via RCON: {last_error}")
