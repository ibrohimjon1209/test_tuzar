from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command

from ai import generate_questions_from_text
from config import settings
from db import ensure_user, get_today_usage_count, init_db, record_document_usage
from extractors import extract_text_from_file

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def send_generated_questions(message: types.Message, text: str, source_label: str) -> None:
    user = message.from_user
    if user is None:
        return

    if get_today_usage_count(user.id) >= settings.daily_limit_per_user:
        await message.answer("Bugunlik limit tugadi. Iltimos, ertaga qayta urinib ko'ring.")
        return

    try:
        await message.answer("Matn qabul qilindi. Savollar yaratilmoqda...")
        cleaned = " ".join(text.split())
        if len(cleaned) < 200:
            raise ValueError("Savol yaratish uchun matn yetarlicha uzun bo'lishi kerak. Iltimos, 2-3 ta gap yoki to'liq paragraf yuboring.")

        q_count = settings.default_question_count
        if len(cleaned) > 20000:
            cleaned = cleaned[:20000]

        all_questions = generate_questions_from_text(cleaned, language=settings.bot_language, question_count=q_count)
        if not all_questions:
            raise ValueError("Savollar yaratilmadi.")

        total = min(len(all_questions), q_count)
        for idx, item in enumerate(all_questions[:total], start=1):
            options = "\n".join(f"{chr(65 + j)}. {opt}" for j, opt in enumerate(item["options"]))
            await message.answer(f"<b>{idx}. {item['question']}</b>\n\n{options}")

        answer_key_lines = []
        for idx, item in enumerate(all_questions[:total], start=1):
            correct_letter = chr(65 + int(item["correct_index"]))
            answer_key_lines.append(f"{idx}. {correct_letter} — {item['options'][int(item['correct_index'])]}. {item['explanation']}")

        if answer_key_lines:
            await message.answer("<b>Javoblar kaliti:</b>\n" + "\n".join(answer_key_lines))

        record_document_usage(user.id, source_label, total, "success")
        await message.answer(f"✅ Tayyor. Yaratilgan savollar soni: {total}")
    except Exception as exc:
        record_document_usage(user.id, source_label, 0, "error")
        await message.answer(f"Xatolik yuz berdi: {exc}")


@dp.message(Command("start"))
async def start_handler(message: types.Message) -> None:
    user = message.from_user
    if user is not None:
        ensure_user(user.id, user.full_name, user.username)
    await message.answer(
        "<b>Assalomu alaykum, Dilshodbek domla! \n\n</b>"
"-TestTuzar botga xush kelibsiz!\n"

"-Matn yuboring yoki .txt, .docx, .pdf fayl jo‘nating.\n"

"-Bot material asosida test savol tuzadi (savollar soni mavzu hajmiga qarab).\n\n\n"

"SE: @se_nsdcorp @nsd_corporation"
    )


@dp.message(Command("help"))
async def help_handler(message: types.Message) -> None:
    await message.answer(
        "Yordam:\n"
        "- Matn yuboring: bot 10 ta A/B/C/D savol yaratadi\n"
        "- .txt, .docx yoki .pdf fayl yuboring\n"
        "- Kunniy cheklov: 10 ta so'rov"
    )


@dp.message(F.text)
async def text_handler(message: types.Message) -> None:
    if message.text is None or message.text.startswith("/"):
        return
    if message.from_user is None:
        return
    ensure_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    await send_generated_questions(message, message.text, "text_input")


@dp.message(F.document)
async def document_handler(message: types.Message) -> None:
    if message.from_user is None:
        return

    user_id = message.from_user.id
    ensure_user(user_id, message.from_user.full_name, message.from_user.username)

    if get_today_usage_count(user_id) >= settings.daily_limit_per_user:
        await message.answer("Bugunlik limit tugadi. Iltimos, ertaga qayta urinib ko'ring.")
        return

    document = message.document
    allowed = {
        "text/plain",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    if document.mime_type not in allowed:
        await message.answer("Faqat .txt, .pdf yoki .docx fayllari qabul qilinadi.")
        return

    if document.file_size and document.file_size > settings.max_file_size_mb * 1024 * 1024:
        await message.answer(f"Fayl hajmi {settings.max_file_size_mb} MB dan kichik bo'lishi kerak.")
        return

    try:
        await message.answer("Fayl qabul qilindi. Matn ajratilmoqda va savollar yaratilmoqda...")
        file = await bot.get_file(document.file_id)
        local_path = Path(f"/tmp/{document.file_name or 'document'}")
        local_path.parent.mkdir(parents=True, exist_ok=True)
        await bot.download_file(file.file_path, str(local_path))

        text = extract_text_from_file(local_path)
        await send_generated_questions(message, text, document.file_name or "document")
    except Exception as exc:
        record_document_usage(user_id, document.file_name or "document", 0, "error")
        await message.answer(f"Xatolik yuz berdi: {exc}")


async def main() -> None:
    init_db()
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, handle_signals=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Shutting down bot.")
