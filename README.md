# DocToTest Bot

Telegram bot uchun Python 3.11+ loyiha. Bot matn yoki `.docx`/`.pdf` fayldan savollar yaratadi, O'zbek tilida A/B/C/D formatda javoblar beradi va Telegram'da ko'rsatadi.

## Texnik tanlov

- Python 3.11+
- aiogram 3
- Gemini API
- SQLite (MVP)
- Docker

## Ishga tushirish

1. Virtual environment yarating:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Bog'liqliklarni o'rnating:
   ```bash
   pip install -r requirements.txt
   ```

3. `.env` yarating va faylga token va API keyni kiriting:
   ```bash
   copy .env.example .env
   ```

4. `.env` ichida quyidagilar bo'lishi kerak:
   - `BOT_TOKEN`
   - `GEMINI_API_KEY`
   - `GEMINI_MODEL=gemini-3.8-flash`
   - `BOT_LANGUAGE=uz`
   - `DEFAULT_QUESTION_COUNT=10`

5. Loyiha boshlanadi:
   ```bash
   python main.py
   ```

## Botdan foydalanish

- Matn yuboring, bot avtomatik 10 ta savol yaratadi.
- `.docx` yoki `.pdf` fayl yuborish ham ishlaydi.
- Savollar A/B/C/D ko'rinishida keladi.
- Faqat O'zbek tilida ishlab turadi.

## Struktura

- `main.py` — bot entry point va text/file handler
- `config.py` — env va sozlamalar
- `extractors.py` — DOCX/PDF matn ajratish
- `chunker.py` — text chunking
- `ai.py` — Gemini + strict JSON validation
- `db.py` — SQLite kunlik limit va hisobot
- `exporters.py` — Word export uchun MVP

## Server/Docker deploy

Loyiha Docker + polling rejimida serverga qo'yilishi uchun tayyor. Batafsil buyruqlarni [DEPLOY.md](DEPLOY.md) faylida ko'ring.

```bash
cp .env.example .env
# .env ni to'ldiring

docker compose up -d --build
```

## Eslatma

Bu loyiha lokal MVP bo'lib, keyinchalik OCR, PDF export, kuchliroq validation va kengaytirilgan deploy bosqichlari uchun moslanishi mumkin.
"# test_tuzar" 
