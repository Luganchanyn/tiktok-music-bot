import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config import BOT_TOKEN, DOWNLOADS_DIR
from music_recognizer import MusicRecognizer
from downloader import TikTokDownloader

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
recognizer = MusicRecognizer()
downloader = TikTokDownloader()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для определения музыки из TikTok.\n\n"
        "Отправь мне:\n"
        "1️⃣ Ссылку на TikTok видео\n"
        "2️⃣ Или загрузи видео напрямую\n\n"
        "И я определю, какая музыка играет! 🎵"
    )


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "🔍 Как пользоваться ботом:\n\n"
        "1. Отправьте ссылку на TikTok видео\n"
        "2. Или загрузите видео файл\n"
        "3. Подождите немного, пока я анализирую музыку\n"
        "4. Получите информацию о треке!\n\n"
        "⚠️ Важно: видео должно содержать музыку достаточной длительности и качества для распознавания"
    )


@dp.message()
async def handle_message(message: types.Message):
    try:
        if message.text and "tiktok.com" in message.text:
            # Обработка ссылки на TikTok
            status_message = await message.answer("⏳ Загружаю видео...")
            video_path = await downloader.download_video(message.text)

            if not video_path:
                await status_message.edit_text("❌ Не удалось загрузить видео. Проверьте ссылку.")
                return

            await status_message.edit_text("🎵 Анализирую музыку...")
            result = await recognizer.recognize_from_file(video_path)

            if result:
                response = (
                    f"✨ Найдена музыка!\n\n"
                    f"🎵 Название: {result['title']}\n"
                    f"👤 Исполнитель: {result['artist']}\n"
                    f"💿 Альбом: {result['album']}\n\n"
                )

                if result.get('spotify_url'):
                    response += f"🎧 Слушать в Spotify: {result['spotify_url']}\n"
                if result.get('apple_music_url'):
                    response += f"🎵 Слушать в Apple Music: {result['apple_music_url']}\n"

                await status_message.edit_text(response)
            else:
                await status_message.edit_text("❌ Не удалось распознать музыку. Попробуйте другое видео.")

            # Очистка временных файлов
            if os.path.exists(video_path):
                os.remove(video_path)

        elif message.video or message.document:
            # Обработка загруженного видео
            status_message = await message.answer("⏳ Обрабатываю видео...")

            file_id = message.video.file_id if message.video else message.document.file_id
            file = await bot.get_file(file_id)

            # Сохраняем видео во временный файл
            video_path = os.path.join(DOWNLOADS_DIR, f"{file.file_id}.mp4")
            await bot.download_file(file.file_path, video_path)

            await status_message.edit_text("🎵 Анализирую музыку...")
            result = await recognizer.recognize_from_file(video_path)

            if result:
                response = (
                    f"✨ Найдена музыка!\n\n"
                    f"🎵 Название: {result['title']}\n"
                    f"👤 Исполнитель: {result['artist']}\n"
                    f"💿 Альбом: {result['album']}\n\n"
                )

                if result.get('spotify_url'):
                    response += f"🎧 Слушать в Spotify: {result['spotify_url']}\n"
                if result.get('apple_music_url'):
                    response += f"🎵 Слушать в Apple Music: {result['apple_music_url']}\n"

                await status_message.edit_text(response)
            else:
                await status_message.edit_text("❌ Не удалось распознать музыку. Попробуйте другое видео.")

            # Очистка временных файлов
            if os.path.exists(video_path):
                os.remove(video_path)

        else:
            await message.answer(
                "🤔 Отправьте мне ссылку на TikTok видео или загрузите видео файл"
            )

    except Exception as e:
        logging.error(f"Error processing message: {e}")
        await message.answer("😔 Произошла ошибка при обработке запроса. Попробуйте позже.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())