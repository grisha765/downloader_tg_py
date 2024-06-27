import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from youtube.download import download_audio, download_video, get_video_info
from config.config import Config
from config import logging_config

logging = logging_config.setup_logging(__name__)

url_list = {}
media_cache = {}
channel_id = Config.tg_channel_id

app = Client("bot", api_id=Config.tg_id, api_hash=Config.tg_hash, bot_token=Config.tg_token)

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Привет! Отправь мне ссылку на видео.")
    logging.debug(f"User {message.from_user.id} started the bot")

async def send_to_channel(file_path: str):
    file_extension = os.path.splitext(file_path)[1].lower()
    try:
        logging.debug(f"Отправка {file_path} в канал {channel_id}")
        if file_extension in ['.mp4', '.webm', '.mkv']:
            file_send = await app.send_video(channel_id, file_path)
            logging.debug(f"Видео {file_path} успешно отправлено в канал {channel_id}")
        elif file_extension in ['.mp3', '.wav', '.ogg']:
            file_send = await app.send_audio(channel_id, file_path)
            logging.debug(f"Аудио {file_path} успешно отправлено в канал {channel_id}")
        else:
            logging.warning(f"Формат файла {file_extension} не поддерживается для отправки.")
        os.remove(file_path)
        return file_send
    except Exception as e:
        logging.error(f"Ошибка при отправке файла: {e}")
        return None

@app.on_message(filters.text & filters.private)
async def handle_link(client, message):
    try:
        url = message.text
        url_list[message.from_user.id] = url
        logging.debug(f"URL получен от пользователя {message.from_user.id}: {url}")

        send_message = await message.reply("Получение информации об видео...")
        if url.startswith("https://"):
            info = await get_video_info(url)
            logging.debug(f"Информация о видео получена: {info}")

            name = info["name"]
            duration = info["duration"]
            description = info["description"]
            author = info["author"]
            date = info["date"]
            qualities = info["qualities"]
            thumbnail = info["thumbnail"]

            buttons = [InlineKeyboardButton(f"{quality}", callback_data=f"quality_{quality.split(' - ')[0]}") for quality in qualities]
            buttons.append(InlineKeyboardButton("Audio", callback_data="audio"))

            reply_markup = InlineKeyboardMarkup([[button] for button in buttons])
            if thumbnail:
                await send_message.reply_photo(photo=thumbnail, caption=f"{name}\nОписание:\n{description}\nАвтор: {author}\nДата выхода: {date}\nПродолжительность: {duration}\nВыберите качество:", reply_markup=reply_markup)
                await send_message.delete()
            else:
                await send_message.edit_text(
                    f"Название: {name}\nОписание:\n```{description}```\nАвтор: {author}\nДата выхода: {date}\nПродолжительность: {duration}\nВыберите качество:", reply_markup=reply_markup
                )
        else:
            await send_message.edit_text("Пожалуйста, отправьте корректную ссылку, начинающуюся с 'https://'.")
            logging.warning(f"Некорректный URL получен от пользователя {message.from_user.id}: {url}")

    except Exception as e:
        logging.error(f"Ошибка при обработке ссылки: {e}")

@app.on_callback_query(filters.regex(r"^quality_(.*)$"))
async def handle_quality_choice(client, callback_query):
    try:
        quality = callback_query.data.split("_")[1]
        url = url_list[callback_query.from_user.id]
        logging.debug(f"Пользователь {callback_query.from_user.id} выбрал качество {quality} для URL {url}")

        cache_key = f"{url}_{quality}"
        if cache_key in media_cache:
            message_id = media_cache[cache_key]
            logging.debug(f"Видео в качестве {quality} для URL {url} найдено в кеше")
            await app.forward_messages(callback_query.message.chat.id, channel_id, message_id, drop_author=True)
        else:
            info = await get_video_info(url)
            qualities = [q.split(' - ')[0] for q in info["qualities"]]

            if quality in qualities:
                info_send = await callback_query.message.reply_text(f"Видео в качестве {quality} загружается.")
                await callback_query.answer()
                file = await download_video(url, quality)
                message_sent = await send_to_channel(file)
                if message_sent:
                    media_cache[cache_key] = message_sent.id
                    logging.debug(f"Видео в качестве {quality} для URL {url} добавлено в кеш")
                    await info_send.delete()
                    await app.forward_messages(callback_query.message.chat.id, channel_id, message_sent.id, drop_author=True)
            else:
                await callback_query.message.edit_text("Выбранное качество недоступно!")
                logging.warning(f"Выбранное качество {quality} недоступно для URL {url}")

        del url_list[callback_query.from_user.id]
        logging.debug(f"URL удален из списка запросов для пользователя {callback_query.from_user.id}")

    except Exception as e:
        logging.error(f"Ошибка при обработке выбора качества: {e}")
        await callback_query.answer()

@app.on_callback_query(filters.regex(r"^audio$"))
async def handle_audio_choice(client, callback_query):
    try:
        url = url_list[callback_query.from_user.id]
        logging.debug(f"Пользователь {callback_query.from_user.id} выбрал аудио для URL {url}")

        cache_key = f"{url}_audio"
        if cache_key in media_cache:
            message_id = media_cache[cache_key]
            logging.debug(f"Аудио для URL {url} найдено в кеше")
            await app.forward_messages(callback_query.message.chat.id, channel_id, message_id, drop_author=True)
        else:
            info_send = await callback_query.message.reply_text("Аудио загружается.")
            await callback_query.answer()
            file = await download_audio(url)
            message_sent = await send_to_channel(file)
            if message_sent:
                media_cache[cache_key] = message_sent.id
                logging.debug(f"Аудио для URL {url} добавлено в кеш")
                await info_send.delete()
                await app.forward_messages(callback_query.message.chat.id, channel_id, message_sent.id, drop_author=True)

        del url_list[callback_query.from_user.id]
        logging.debug(f"URL удален из списка запросов для пользователя {callback_query.from_user.id}")

    except Exception as e:
        logging.error(f"Ошибка при обработке выбора аудио: {e}")
        await callback_query.answer()

def run_bot():
    logging.info("Запуск бота...")
    app.run()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

