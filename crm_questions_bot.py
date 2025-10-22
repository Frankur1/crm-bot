import os
import json
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------ ⚙️ НАСТРОЙКИ ------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_SHEET_NAME = "Вопросы СРМ"
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
# --------------------------------------------------

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден. Добавь его в Railway Variables.")
if not GOOGLE_CREDENTIALS:
    raise ValueError("❌ GOOGLE_CREDENTIALS не найден. Добавь его в Railway Variables.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)

# ------------------ 🔐 ПОДКЛЮЧЕНИЕ GOOGLE ------------------
try:
    # Если Railway убрал двойные слэши, возвращаем их обратно
    fixed_json = GOOGLE_CREDENTIALS.replace('\\n', '\n')
    creds_json = json.loads(fixed_json)

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    logging.info("✅ Успешно подключено к таблице '%s'", GOOGLE_SHEET_NAME)
except Exception as e:
    logging.error("❌ Ошибка при подключении к Google Sheets: %s", e)
    raise

# ------------------ 🤖 НАСТРОЙКА БОТА ------------------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "👋 Привет!\n\n"
        "Я бот для сбора вопросов по обучению CRM 💬\n"
        "Просто напиши сюда свой вопрос — и я сохраню его для команды.\n\n"
        "Можно отправлять несколько вопросов подряд, каждый сохранится отдельно ✅"
    )

@dp.message(Command("info"))
async def info(message: types.Message):
    await message.answer(
        "📘 Все вопросы сохраняются в Google Таблицу *«Вопросы СРМ»*, "
        "чтобы команда могла заранее подготовиться.\n\n"
        "Отправь свой вопрос прямо сюда 👇",
        parse_mode="Markdown"
    )

@dp.message()
async def collect_question(message: types.Message):
    user = message.from_user
    question = message.text.strip()

    try:
        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user.full_name or "-",
            f"@{user.username}" if user.username else "-",
            user.id,
            question
        ])
        logging.info("💾 Вопрос от %s (%s): %s", user.full_name, user.id, question)
        await message.answer("✅ Вопрос сохранён! Спасибо 🙌")

    except Exception as e:
        logging.error("❌ Ошибка при сохранении вопроса: %s", e)
        await message.answer("⚠️ Не удалось сохранить вопрос. Попробуй позже.")

async def main():
    logging.info("🤖 Бот запущен и ожидает сообщений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
