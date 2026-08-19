# Xray — VLESS + TCP + SOCKS (ساده)

بدون TLS، بدون Reality، بدون WS.

## هر دو سرور

| inbound | پورت | توضیح |
|---------|------|--------|
| VLESS | `8443` | TCP plain |
| SOCKS | `1080` | فقط localhost |

| outbound | مقصد |
|----------|------|
| ایران | VLESS → آلمان |
| آلمان | VLESS → ایران |

## تست

```bash
# از ایران — خروجی IP آلمان
curl --socks5-hostname 127.0.0.1:1080 http://ifconfig.me

# از آلمان — خروجی IP ایران
curl --socks5-hostname 127.0.0.1:1080 http://ifconfig.me
```

## Deploy

```bash
python3 scripts/setup_xray.py
```

## فایل‌های کانفیگ

- `configs/xray/iran.config.json`
- `configs/xray/germany.config.json`
