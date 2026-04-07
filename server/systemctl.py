from typing import Callable


MINECRAFT_ADMIN_SERVICE = "minecraft-admin"


def restart_minecraft_admin(run_cmd: Callable[[list[str]], str]) -> dict:
    run_cmd(["sudo", "systemctl", "restart", MINECRAFT_ADMIN_SERVICE])
    return {"ok": True, "service": MINECRAFT_ADMIN_SERVICE, "action": "restart"}
