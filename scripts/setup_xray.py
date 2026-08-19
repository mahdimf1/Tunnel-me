#!/usr/bin/env python3
"""Install Docker and deploy Xray on Iran/Germany servers."""

from __future__ import annotations

import json
import secrets
import sys
import textwrap
import uuid
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / "secrets" / ".env"

IRAN_DAEMON = """{
  "registry-mirrors": [
    "https://docker.iranserver.com",
    "https://registry.docker.ir"
  ],
  "insecure-registries": ["127.0.0.1:5000"]
}"""


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
    code = stdout.channel.recv_exit_status()
    return code, out, err


def upload_text(client: paramiko.SSHClient, remote_path: str, content: str) -> None:
    sftp = client.open_sftp()
    Path_remote = remote_path.rsplit("/", 1)[0]
    run(client, f"mkdir -p {Path_remote}")
    with sftp.file(remote_path, "w") as handle:
        handle.write(content)
    sftp.close()


def ensure_docker(host: str, env: dict[str, str], *, iran: bool) -> None:
    client = ssh(host, env)
    code, out, _ = run(client, "docker --version 2>/dev/null || echo MISSING")
    if "MISSING" in out:
        print(f"[{host}] installing docker...")
        if iran:
            run(
                client,
                "apt-get update -qq && "
                "DEBIAN_FRONTEND=noninteractive apt-get install -y -qq ca-certificates curl gnupg 2>/dev/null",
            )
            run(client, "curl -fsSL https://get.docker.com | sh", timeout=600)
        else:
            run(client, "curl -fsSL https://get.docker.com | sh", timeout=600)
    else:
        print(f"[{host}] docker already installed: {out.strip()}")

    if iran:
        upload_text(client, "/etc/docker/daemon.json", IRAN_DAEMON)
        run(client, "systemctl enable docker", timeout=60)
        run(client, "systemctl restart docker", timeout=120)

    code, out, err = run(client, "systemctl is-active docker", timeout=60)
    print(f"[{host}] docker status:\n{out}{err}")
    client.close()


def deploy_xray(host: str, env: dict[str, str], config: str, *, iran: bool) -> None:
    client = ssh(host, env)
    compose = (ROOT / "configs/xray/docker-compose.yml").read_text()
    run(client, "mkdir -p /opt/xray/config")
    upload_text(client, "/opt/xray/docker-compose.yml", compose)
    upload_text(client, "/opt/xray/config/config.json", config)

    if iran:
        print(f"[{host}] pulling xray image via Iranian mirrors...")
        code, out, err = run(client, "docker pull teddysun/xray:latest", timeout=600)
        if code != 0:
            print(f"[{host}] mirror pull failed, trying direct pull...\n{err}")
            run(client, "docker pull teddysun/xray:latest", timeout=600)
    else:
        run(client, "docker pull teddysun/xray:latest", timeout=600)

    run(client, "cd /opt/xray && docker compose down 2>/dev/null; docker compose up -d")
    code, out, err = run(client, "docker ps --filter name=xray --format '{{.Names}} {{.Status}}'")
    print(f"[{host}] xray container:\n{out or err}")
    client.close()


def main() -> None:
    env = load_env()
    xray_uuid = str(uuid.uuid4())

    server_cfg = (
        (ROOT / "configs/xray/server.config.json")
        .read_text()
        .replace("__UUID__", xray_uuid)
    )
    client_cfg = (
        (ROOT / "configs/xray/client.config.json")
        .read_text()
        .replace("__UUID__", xray_uuid)
        .replace("__GERMANY_HOST__", env["GERMANY_HOST"])
    )

    (ROOT / "configs/xray/generated").mkdir(exist_ok=True)
    (ROOT / "configs/xray/generated/server.config.json").write_text(server_cfg)
    (ROOT / "configs/xray/generated/client.config.json").write_text(client_cfg)
    (ROOT / "configs/xray/generated/credentials.json").write_text(
        json.dumps({"uuid": xray_uuid, "port": 8443}, indent=2)
    )

    ensure_docker(env["GERMANY_HOST"], env, iran=False)
    ensure_docker(env["IRAN_HOST"], env, iran=True)
    deploy_xray(env["GERMANY_HOST"], env, server_cfg, iran=False)
    deploy_xray(env["IRAN_HOST"], env, client_cfg, iran=True)

    client = ssh(env["GERMANY_HOST"], env)
    code, out, err = run(client, "ss -tlnp | grep 8443 || docker logs xray --tail 20")
    print(f"[germany] port 8443:\n{out}{err}")
    client.close()

    client = ssh(env["IRAN_HOST"], env)
    code, out, err = run(
        client,
        "curl -s --connect-timeout 5 --socks5-hostname 127.0.0.1:1080 http://ifconfig.me || true",
    )
    print(f"[iran] socks test via xray:\n{out}{err}")
    client.close()

    print(f"\nXray UUID: {xray_uuid}")


if __name__ == "__main__":
    main()
