# Tunnel-me

پروژه راه‌اندازی و مدیریت ارتباط امن بین دو سرور.

## هدف

ایجاد تونل/ارتباط پایدار بین **سرور ۱** و **سرور ۲** برای دسترسی به سرویس‌های موردنیاز (مثلاً Docker Registry، SSH، یا سرویس‌های داخلی).

## قانون اصلی

> **همه سرویس‌ها داخل Docker container اجرا می‌شوند** — نه مستقیم روی سرور.
> جزئیات: [`docs/conventions.md`](docs/conventions.md)

## وضعیت

| مرحله | وضعیت |
|-------|--------|
| Docker روی هر دو سرور | ✅ |
| Xray (ایران ↔ آلمان) | ✅ |
| Docker Registry + tunnel | ✅ |
| WireGuard | ❌ UDP block |

## ساختار پروژه

```
Tunnel-me/
├── README.md
├── AGENTS.md               # دستورالعمل برای agent
├── docs/
│   ├── conventions.md      # قوانین container-first
│   ├── servers.md
│   ├── plan.md
│   └── xray.md
├── configs/
│   ├── xray/
│   ├── docker-compose.registry.yml
│   └── registry-tunnel/
└── scripts/
```

## مخزن

- GitHub: https://github.com/mahdimf1/Tunnel-me

## نکات امنیتی

- کلیدها، پسوردها و tokenها در این مخزن commit **نمی‌شوند**
- فایل‌های حساس در `.gitignore` قرار دارند
- از `.env.example` برای نمونه متغیرها استفاده می‌شود
