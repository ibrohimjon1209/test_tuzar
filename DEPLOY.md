# Serverga deploy qilish (Ubuntu + Docker + polling)

Ushbu loyiha polling rejimida ishlaydi. Telegram webhook ishlatmaysiz, shuning uchun serverga faqat SSH ochiladi.

## 1) Oracle Cloud Always Free VM yaratish

1. Oracle Cloudga kirib, `Always Free` VM yaratish sahifasiga o'ting.
2. Ubuntu 22.04 yoki 24.04 ni tanlang.
3. Shape sifatida `VM.Standard.A1.Flex` yoki Always Free AMD variantni tanlang.
4. SSH kalit yarating va `.pem` faylni yuklang.
5. Eslatma: ba'zan ro'yxatdan o'tishda xalqaro karta tekshiruvi ishlashi mumkin; agar Uzcard/Humo ishlamasa, rasmiy saytga qayta tekshirish kerak bo'ladi.
6. Kiruvchi portlar faqat SSH (22) qolsin.

## 2) Server xavfsizligi

```bash
sudo apt update && sudo apt upgrade -y
sudo adduser --disabled-password --gecos "" deploy
sudo usermod -aG sudo deploy
```

SSH bilan kalit orqali kirishni tekshirib oling:

```bash
ssh -i <key.pem> deploy@<server_ip>
```

Keyin root login va parol bilan SSHni o'chirish:

```bash
sudo nano /etc/ssh/sshd_config
```

Quyidagi qatorlarni tekshiring:

```bash
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

Keyin:

```bash
sudo systemctl restart sshd
```

UFW ni yoqing (faqat 22):

```bash
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

Unattended upgrades o'rnatish (ixtiyoriy, lekin tavsiya etiladi):

```bash
sudo apt install -y unattended-upgrades apt-listchanges
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

## 3) Docker va Docker Compose o'rnatish

Rasmiy Docker repo bo'yicha o'rnating:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

## 4) Loyihani serverga olib borish

Git orqali yoki `scp/rsync` bilan serverga ko'chiring:

```bash
git clone <repo_url> bot-project
cd bot-project
```

Yoki:

```bash
scp -r . deploy@<server_ip>:/home/deploy/bot-project
```

`.env` ni serverda qo'lda yarating:

```bash
cp .env.example .env
nano .env
chmod 600 .env
```

`BOT_TOKEN`, `GEMINI_API_KEY` va boshqa qiymatlarni kiriting. Tokenlar logga yozilmasin.

## 5) Ishga tushirish

```bash
docker compose up -d --build
```

Loglarni ko'rish:

```bash
docker compose logs -f --tail=100 bot
```

Statusni tekshirish:

```bash
docker ps
```

## 6) Yangilash

```bash
git pull
# yoki fayllarni yangilang

docker compose up -d --build
```

## 7) Telegram bilan qarama-qarshiliklar va muammolar

1. Bot token bir xil polling ishlatiladi. Serverga ishga tushirishdan oldin kompyuterdagi `python main.py` to'xtatilishi kerak.
2. TelegramConflictError oldini olish uchun `bot.delete_webhook(drop_pending_updates=True)` ishlatiladi.
3. `getWebhookInfo` tekshirish:

```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

Agar `result.url` bo'sh bo'lsa, polling ishlayotgan bo'ladi.

## 8) Muammolar jadvali

- 503: Gemini band / vaqtincha xizmat mavjud emas; qayta urinib ko'ring, fallback model ishlaydi.
- 429: Gemini kvotasi tugagan; bitta model yoki key bilan sinab ko'ring.
- Conflict: bot avval ishlayotgan joyda polling ishlayotgan bo'lishi mumkin.
- DB permission denied: `/data` volume not writable, container user yoki volume egasini tekshirish.
- Bot javob bermayapti: `docker compose logs -f --tail=200 bot`.
- Disk to'ldi: `df -h`, `docker system df`.

## 9) Always Free serverda ehtiyot choralari

Oracle Cloud Always Free instance ba'zan resurslar bo'sh turganini tekshirish shart. Agar CPU, tarmoq yoki disk juda past bo'lsa, xizmat vaqtincha to'xtashi mumkin. Buni "pul to'laylik" yoki "serverni yutib olamiz" deb o'ylab qilmang. Zaxira bo'lsin: `backup.sh` ni cron bilan tekshiring va boshqa arzon VPS yoki cloud rejasiga tayyorgarlik ko'ring.

## 10) Bepul platformalar haqida

Render, Railway va boshqa bepul platformalar fayl tizimi doimiy bo'lmasligi mumkin. Ular uchun ma'lumotlar saqlash xatolarga olib kelishi mumkin. Shuning uchun loyiha server yoki VPS va Docker ustida ishlash uchun optimallashtirilgan.
