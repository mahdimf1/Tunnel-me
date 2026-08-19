#!/usr/bin/env python3
"""Deploy simple VLESS+TCP and SOCKS on both servers."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / "secrets" / ".env"
COMPOSE = ROOT / "configs/xray/docker-compose.yml"


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def ssh(host: str, env: dict[str, str]) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        host,
        username=env["SSH_USER"],
        password=env["SSH_PASS"],
        timeout=25,
        allow_agent=False,
        look_for_keys=False,
    )
    return client


def run(client: paramiko.SSHClient, cmd: str, timeout: int = 300) -> tuple[int, str, str]:
    _, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    return stdout.channel.recv_exit_status(), out, err


def upload(client: paramiko.SSHClient, path: str, content: str) -> None:
    run(client, f"mkdir -p {path.rsplit('/', 1)[0]}")
    sftp = client.open_sftp()
    with sftp.file(path, "w") as handle:
        handle.write(content)
    sftp.close()


def deploy(host: str, config: str, env: dict[str, str], *, iran: bool) -> None:
    client = ssh(host, env)
    upload(client, "/opt/xray/docker-compose.yml", COMPOSE.read_text())
    upload(client, "/opt/xray/config/config.json", config)

    if iran:
        run(client, "docker pull teddysun/xray:latest", timeout=600)
    else:
        run(client, "docker pull teddysun/xray:latest", timeout=600)

    run(client, "cd /opt/xray && docker compose down 2>/dev/null; docker compose up -d")
    _, out, err = run(client, "docker ps --filter name=xray --format '{{.Names}} {{.Status}}'; docker logs xray --tail 3 2>&1")
    print(f"[{host}]\n{out or err}")
    client.close()


def main() -> None:
    env = load_env()
    xray_uuid = str(uuid.uuid4())

    germany_cfg = (
        (ROOT / "configs/xray/germany.config.json")
        .read_text()
        .replace("__UUID__", xray_uuid)
        .replace("__IRAN_HOST__", env["IRAN_HOST"])
    )
    iran_cfg = (
        (ROOT / "configs/xray/iran.config.json")
        .read_text()
        .replace("__UUID__", xray_uuid)
        .replace("__GERMANY_HOST__", env["GERMANY_HOST"])
    )

    generated = ROOT / "configs/xray/generated"
    generated.mkdir(exist_ok=True)
    (generated / "germany.config.json").write_text(germany_cfg)
    (generated / "iran.config.json").write_text(iran_cfg)
    (generated / "credentials.json").write_text(
        json.dumps(
            {
                "uuid": xray_uuid,
                "vless_port": 8443,
                "socks_port": 1080,
                "network": "tcp",
                "tls": False,
            },
            indent=2,
        )
    )

    deploy(env["GERMANY_HOST"], germany_cfg, env, iran=False)
    deploy(env["IRAN_HOST"], iran_cfg, env, iran=True)

    client = ssh(env["IRAN_HOST"], env)
    _, out, _ = run(client, "curl -s --connect-timeout 8 --socks5-hostname 127.0.0.1:1080 http://ifconfig.me")
    print(f"[iran socks -> germany] {out.strip()}")
    client.close()

    client = ssh(env["GERMANY_HOST"], env)
    _, out, _ = run(client, "curl -s --connect-timeout 8 --socks5-hostname 127.0.0.1:1080 http://ifconfig.me")
    print(f"[germany socks -> iran] {out.strip()}")
    client.close()

    print(f"\nUUID: {xray_uuid}")


if __name__ == "__main__":
    main()
