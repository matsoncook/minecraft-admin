from fastapi import FastAPI, HTTPException
import subprocess

from server.kick import kick_server_player
from server.player import get_server_players
from server.systemctl import restart_minecraft_admin

app = FastAPI()

SERVICE_NAME = "minecraft-1.20.1-forge.service"

def run_cmd(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr.strip())
    return result.stdout.strip()

@app.get("/api/server/status")
def server_status():
    output = run_cmd(["systemctl", "is-active", SERVICE_NAME])
    return {"status": output}

@app.post("/api/server/start")
def server_start():
    run_cmd(["sudo", "systemctl", "start", SERVICE_NAME])
    return {"ok": True}

@app.post("/api/server/stop")
def server_stop():
    run_cmd(["sudo", "systemctl", "stop", SERVICE_NAME])
    return {"ok": True}

@app.post("/api/server/restart")
def server_restart():
    run_cmd(["sudo", "systemctl", "restart", SERVICE_NAME])
    return {"ok": True}

@app.get("/api/server/logs")
def server_logs():
    output = run_cmd(["journalctl", "-u", SERVICE_NAME, "-n", "50", "--no-pager"])
    return {"logs": output}

@app.get("/api/server/players")
def server_players():
    return get_server_players(run_cmd, SERVICE_NAME)

@app.post("/api/server/players/{player_name}/kick")
def server_kick_player(player_name: str, reason: str | None = None):
    try:
        return kick_server_player(run_cmd, SERVICE_NAME, player_name, reason)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.post("/api/systemctl/minecraft-admin/restart")
def systemctl_restart_minecraft_admin():
    try:
        return restart_minecraft_admin(run_cmd)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
