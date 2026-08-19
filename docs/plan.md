# برنامه مرحله‌به‌مرحله

## مرحله ۱ — آماده‌سازی مخزن ✅

- [x] انتخاب مخزن: [mahdimf1/Tunnel-me](https://github.com/mahdimf1/Tunnel-me)
- [x] ایجاد ساختار اولیه پروژه
- [x] Push اولیه به GitHub

## مرحله ۲ — جمع‌آوری اطلاعات سرورها ✅

- [x] ایران: `2.144.13.219`
- [x] آلمان: `91.108.242.106`
- [x] ثبت در `docs/servers.md`

## مرحله ۳ — انتخاب روش تونل ✅

- **Xray VLESS** — تونل TCP بین ایران (client) و آلمان (server)
- **SSH tunnel** — دسترسی به Docker Registry (UDP/WireGuard block بود)
- ~~WireGuard~~ — UDP بین سرورها مسدود است

## مرحله ۴ — پیاده‌سازی ✅

- [x] نصب Docker روی هر دو سرور
- [x] Mirror ایرانی Docker روی سرور ایران
- [x] کانتینر Xray روی آلمان (server) و ایران (client)
- [x] Docker Registry روی آلمان + SSH tunnel از ایران
- [x] تست SOCKS — خروجی IP آلمان از ایران

## مرحله ۵ — نگهداری ⏳

- [ ] اسکریپت‌های deploy/update
- [ ] راهنمای troubleshooting
