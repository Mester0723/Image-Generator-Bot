import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile
from logic import FusionBrainAPI
from config import FUSIONBRAIN_API_KEY, FUSIONBRAIN_SECRET_KEY, BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создаём экземпляр FusionBrain API
fusion = FusionBrainAPI(FUSIONBRAIN_API_KEY, FUSIONBRAIN_SECRET_KEY)

@dp.message(F.text)
async def handle_prompt(message: types.Message):
    prompt = message.text.strip()
    await message.answer("🎨 Генерирую изображение, подожди немного...")

    try:
        # Запускаем синхронный метод в отдельном потоке
        output_path = await asyncio.to_thread(fusion.get_image, prompt, "generated.png")

        # Отправляем пользователю
        photo = FSInputFile(output_path)
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=f"✅ Готово!\nЗапрос: {prompt}")

    except Exception as e:
        await message.answer(f"⚠️ Ошибка при генерации: {e}")

async def main():
    print("🤖 Бот запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())