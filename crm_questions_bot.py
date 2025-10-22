import logging
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ------------------ 🔧 НАСТРОЙКИ ------------------
BOT_TOKEN = "8231175537:AAHySMKxuiiX-_84zhtxrAdw45yebu8erwo"
GOOGLE_SHEET_NAME = "Вопросы СРМ"
CREDENTIALS_FILE = "credentials.json"
# -------------------------------------------------

# Настройка логов
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)

# Авторизация Google Sheets
logging.info("🔐 Подключаемся к Google Sheets...")
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open(GOOGLE_SHEET_NAME).sheet1
logging.info("✅ Успешно подключено к таблице '%s'", GOOGLE_SHEET_NAME)

# Telegram bot
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ------------------ 🤖 ОБРАБОТЧИКИ ------------------

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
        "чтобы команда могла подготовиться заранее.\n\n"
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
        logging.error("❌ Ошибка при записи: %s", e)
        await message.answer("⚠️ Не удалось сохранить вопрос. Попробуй позже.")

# ------------------ 🚀 ЗАПУСК ------------------

async def main():
    logging.info("🤖 Бот запущен и ожидает сообщений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
