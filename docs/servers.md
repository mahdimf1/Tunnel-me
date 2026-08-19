# مشخصات سرورها

> پسورد و secretها در `secrets/.env` (محلی) نگه‌داری می‌شوند — commit نمی‌شوند.

## سرور ۱ — ایران

| مورد | مقدار |
|------|--------|
| نام / نقش | ایران (client) |
| IP | `2.144.13.219` |
| hostname | `i1` |
| سیستم‌عامل | Ubuntu 24.04 LTS |
| SSH | `root@2.144.13.219:22` |
| Docker | ✅ نصب — mirror ایرانی فعال |
| Xray | ✅ client — SOCKS `127.0.0.1:1080` |
| Registry tunnel | ✅ container `registry-tunnel` → `127.0.0.1:5000` |

## سرور ۲ — آلمان

| مورد | مقدار |
|------|--------|
| نام / نقش | آلمان (server) |
| IP | `91.108.242.106` |
| hostname | `dying-aqua.ptr.network` |
| سیستم‌عامل | Ubuntu 24.04.1 LTS |
| SSH | `root@91.108.242.106:22` |
| Docker | ✅ نصب |
| Xray | ✅ server — VLESS `:8443` |
| Docker Registry | ✅ `127.0.0.1:5000` (داخلی) |

## ارتباطات فعال

| مبدأ | مقصد | پورت / پروتکل | توضیح |
|------|------|----------------|--------|
| ایران | آلمان | VLESS TCP `8443` | تونل Xray |
| ایران | localhost | SOCKS `1080` | پروکسی محلی |
| ایران | آلمان | SSH tunnel `5000` | Docker Registry |
| WireGuard | — | UDP `51820/443` | ❌ UDP بین سرورها block است |

## تست اتصال

```bash
# از سرور ایران — خروجی باید IP آلمان باشد
curl --socks5-hostname 127.0.0.1:1080 http://ifconfig.me

# Docker Registry از ایران
curl http://127.0.0.1:5000/v2/
```

## Mirrorهای Docker (ایران)

- `https://docker.iranserver.com`
- `https://registry.docker.ir`
