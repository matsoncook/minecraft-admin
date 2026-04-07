import os
import re
import subprocess
from typing import Callable

ANSI_ESCAPE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def strip_ansi(text: str) -> str:
    return ANSI_ESCAPE.sub("", text)


def _parse_players_from_list_output(output: str) -> tuple[int, list[str]] | None:
    output = strip_ansi(output).strip()

    match = re.search(
        r"There are\s+(\d+)\s+of a max of\s+\d+\s+players online:\s*(.*)",
        output,
        re.IGNORECASE,
    )
    if not match:
        return None

    count = int(match.group(1))
    names_blob = match.group(2).strip()

    if not names_blob:
        return (count, [])

    players = [name.strip() for name in names_blob.split(",") if name.strip()]
    return (count, players)


def _players_from_rcon() -> tuple[int, list[str]] | None:
    password = os.environ.get("MINECRAFT_RCON_PASSWORD")
    print("Recon Password:", "****" if password else "(not set)")
    if not password:
        return None

    host = os.environ.get("MINECRAFT_RCON_HOST", "127.0.0.1")
    port = os.environ.get("MINECRAFT_RCON_PORT", "25575")

    print("Recon Host:", host)
    print("Recon Port:", port)

    rcon_commands = [
        [
            "/home/ubuntu/mcron/mcrcon-0.7.2-linux-x86-64-static/mcrcon",
            "-H",
            host,
            "-P",
            port,
            "-p",
            password,
            "list",
        ],
    ]

    for cmd in rcon_commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print(f"RCON command failed 1: {' '.join(cmd)}")
            continue

        if result.returncode != 0:
            print(f"RCON command failed 2: {' '.join(cmd)}")
            continue

        print(f"RCON command output: {result.stdout.strip()}")
        parsed = _parse_players_from_list_output(result.stdout.strip())
        if parsed is not None:
            return parsed

    return None


def _players_from_journal(
    run_cmd: Callable[[list[str]], str], service_name: str
) -> tuple[int, list[str]]:
    output = run_cmd(["journalctl", "-u", service_name, "-n", "500", "--no-pager"])
    players: set[str] = set()

    for line in output.splitlines():
        if "joined the game" in line:
            joined = re.search(r":\s*([A-Za-z0-9_]{1,16}) joined the game", line)
            if joined:
                players.add(joined.group(1))
        elif "left the game" in line:
            left = re.search(r":\s*([A-Za-z0-9_]{1,16}) left the game", line)
            if left:
                players.discard(left.group(1))

    sorted_players = sorted(players)
    return (len(sorted_players), sorted_players)


def get_server_players(run_cmd: Callable[[list[str]], str], service_name: str) -> dict:
    rcon_players = _players_from_rcon()
    print("RCON Players:", rcon_players)

    if rcon_players is not None:
        count, players = rcon_players
        return {"online": count, "players": players, "source": "rcon"}

    count, players = _players_from_journal(run_cmd, service_name)
    return {
        "online": count,
        "players": players,
        "source": "journal",
        "note": "Using journal fallback. Set MINECRAFT_RCON_PASSWORD for live query.",
    }
