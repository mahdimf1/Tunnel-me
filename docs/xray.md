# راه‌اندازی Xray

## معماری

```
ایران (client)                         آلمان (server)
┌─────────────────┐                   ┌─────────────────┐
│  xray container │ ── VLESS:8443 ──► │  xray container │
│  SOCKS :1080    │                   │  freedom        │
└─────────────────┘                   └─────────────────┘
```

## Deploy

```bash
# از ماشین محلی (با secrets/.env)
python3 scripts/setup_xray.py
```

## فایل‌ها

| فایل | نقش |
|------|-----|
| `configs/xray/server.config.json` | قالب inbound VLESS آلمان |
| `configs/xray/client.config.json` | قالب outbound + SOCKS ایران |
| `configs/xray/docker-compose.yml` | کانتینر `teddysun/xray` |
| `configs/xray/generated/` | کانفیگ‌های generate‌شده (UUID واقعی) |

## تست

```bash
# SOCKS از سرور ایران
curl --socks5-hostname 127.0.0.1:1080 http://ifconfig.me
# باید 91.108.242.106 برگردد

# وضعیت کانتینر
docker ps --filter name=xray
docker logs xray --tail 20
```

## Docker mirror (ایران)

در `/etc/docker/daemon.json`:

```json
{
  "registry-mirrors": [
    "https://docker.iranserver.com",
    "https://registry.docker.ir"
  ]
}
```
