#!/usr/bin/env python3
"""Run commands on Iran/Germany servers using secrets/.env credentials."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import paramiko

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / "secrets" / ".env"


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    if not ENV_FILE.exists():
        raise SystemExit(f"Missing {ENV_FILE}. Copy secrets/.env.example first.")
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def run(host: str, command: str, env: dict[str, str]) -> tuple[int, str, str]:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        host,
        username=env["SSH_USER"],
        password=env["SSH_PASS"],
        timeout=20,
        allow_agent=False,
        look_for_keys=False,
    )
    _, stdout, stderr = client.exec_command(command, timeout=120)
    out = stdout.read().decode()
    err = stderr.read().decode()
    code = stdout.channel.recv_exit_status()
    client.close()
    return code, out, err


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("Usage: remote_exec.py <iran|germany> '<command>'")

    env = load_env()
    target = sys.argv[1]
    command = sys.argv[2]
    host_key = "IRAN_HOST" if target == "iran" else "GERMANY_HOST"
    host = env[host_key]

    code, out, err = run(host, command, env)
    if out:
        sys.stdout.write(out)
    if err:
        sys.stderr.write(err)
    raise SystemExit(code)


if __name__ == "__main__":
    main()
