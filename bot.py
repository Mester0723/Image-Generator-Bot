import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from logic import FusionBrainAPI
from config import BOT_TOKEN, FUSIONBRAIN_API_KEY as API_KEY, FUSIONBRAIN_SECRET_KEY as SECRET_KEY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 🟢 /start и /help
@dp.message(Command(commands=["start", "help"]))
async def cmd_start_help(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    await asyncio.sleep(1.2)
    await message.answer(
        "👋 Привет! Я бот для генерации изображений с помощью **FusionBrain AI** 🧠\n\n"
        "🖼 Просто отправь мне описание картинки, и я создам её!\n\n"
        "📚 Команды:\n"
        "• `/start` — приветствие\n"
        "• `/help` — помощь\n"
        "• Просто напиши описание изображения ✨",
        parse_mode="Markdown"
    )

# 🟣 Генерация изображения
@dp.message()
async def handle_generation(message: types.Message):
    prompt = message.text
    fusion = FusionBrainAPI(api_key=API_KEY, secret_key=SECRET_KEY)

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    status_msg = await message.answer("⏳ Генерирую картинку...")

    try:
        output_path = await asyncio.to_thread(fusion.get_image, prompt, "generated.png")

        await bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
        await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
        await asyncio.sleep(0.5)

        await message.reply_photo(photo=types.FSInputFile(output_path))

        # 🧹 Удаляем файл
        if os.path.exists(output_path):
            os.remove(output_path)
            print(f"🗑️ Удалён временный файл: {output_path}")

    except Exception as e:
        await bot.delete_message(chat_id=message.chat.id, message_id=status_msg.message_id)
        await message.reply(f"⚠️ Ошибка при генерации: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())