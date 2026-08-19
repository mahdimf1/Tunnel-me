# قوانین پروژه

## اصل اول: همه‌چیز داخل کانتینر

**هر برنامه یا سرویسی که نصب/راه‌اندازی می‌شود باید داخل Docker container اجرا شود.**

### چرا؟

- مشکل سرویس = مشکل سرور نیست
- با `docker compose down` یا `docker rm` سریع rollback می‌شود
- نسخه و کانفیگ در Git قابل تکرار است
- وابستگی‌ها روی host آلوده نمی‌شوند

### مجاز روی host

| مورد | دلیل |
|------|------|
| Docker Engine | runtime کانتینرها |
| SSH / firewall پایه | دسترسی مدیریتی |
| فایل‌های کانفیگ در `/opt/<service>/` | mount به کانتینر |

### ممنوع روی host

- نصب مستقیم سرویس‌ها با `apt install nginx`، `pip install`، ...
- `systemd` unit برای اپلیکیشن‌ها (به‌جز Docker)
- WireGuard / OpenVPN / Xray / Registry و ... خارج از container

### الگوی استاندارد

```
/opt/<service>/
├── docker-compose.yml
├── config/          # mount به /etc/<app>
└── data/            # volume پایدار (در صورت نیاز)
```

### دستورات مرسوم

```bash
cd /opt/<service>
docker compose pull
docker compose up -d
docker compose logs -f
docker compose down          # توقف
docker compose down -v       # توقف + حذف volume
```

### سرویس‌های فعلی (همه container)

| سرویس | سرور | مسیر |
|--------|------|------|
| Xray | ایران + آلمان | `/opt/xray/` |
| Docker Registry | آلمان | `/opt/docker-registry/` |
| Registry SSH Tunnel | ایران | `/opt/registry-tunnel/` |
