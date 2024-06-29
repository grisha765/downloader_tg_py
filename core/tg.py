import os
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from youtube.download import download_audio, download_video, get_video_info
from config.config import Config
from config import logging_config
logging = logging_config.setup_logging(__name__)

cache = {}
url_list = {}

app = Client("bot", api_id=Config.tg_id, api_hash=Config.tg_hash, bot_token=Config.tg_token)

def create_quality_buttons(qualities):
    buttons = []
    for quality in qualities:
        quality_number = re.match(r'(\d+)', quality).group(1)
        buttons.append([InlineKeyboardButton(quality, callback_data=f'quality_{quality_number}')])
    buttons.append([InlineKeyboardButton("Audio", callback_data='audio')])
    return InlineKeyboardMarkup(buttons)

@app.on_message(filters.text & filters.private)
async def handle_message(client, message):
    text = message.text
    user_id = message.from_user.id
    logging.debug(f"Received message: {text}")

    url_pattern = r'(https?://(?:www\.|m\.)?youtube\.com/watch\?v=[\w-]+|https?://youtu\.be/[\w-]+)'
    urls = re.findall(url_pattern, text)
    
    logging.debug(f"Found URLs: {urls}")

    if urls:
        for url in urls:
            url_list[user_id] = url  # Save the URL for the user
            video_info = await get_video_info(url)
            logging.debug(f"Video info for {url}: {video_info}")
            
            qualities = video_info.get('qualities', [])
            if qualities:
                reply_markup = create_quality_buttons(qualities)
                message_text = f"""
**Название**: {video_info['name']}
**Автор**: {video_info['author']}
**Дата выхода**: {video_info['date']}
**Продолжительность**: {video_info['duration']}
                """
                await message.reply_photo(photo=video_info['thumbnail'], caption=message_text, reply_markup=reply_markup)
    else:
        logging.debug("No URLs found in the message.")

@app.on_callback_query(filters.regex(r'^quality_\d+$'))
async def handle_quality_selection(client, callback_query: CallbackQuery):
    quality = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    logging.debug(f"Selected quality: {quality}")

    url = url_list.get(user_id)
    if not url:
        await callback_query.answer("URL not found.")
        return

    cache_key = (url, quality)
    if cache_key in cache:
        await callback_query.answer("Sending cached video...")
        cached_message_id = cache[cache_key]
        await app.forward_messages(
            chat_id=callback_query.message.chat.id, 
            from_chat_id=cached_message_id[0], 
            message_ids=cached_message_id[1],
            drop_author=True
        )
    else:
        await callback_query.answer(f"Selected quality: {quality}")
        file_name = await download_video(url, quality)
        logging.debug(f"Downloaded file: {file_name}")
        sent_message = await app.send_video(
            chat_id=callback_query.message.chat.id, 
            video=file_name, 
            caption=f"{quality}"
        )
        cache[cache_key] = (callback_query.message.chat.id, sent_message.id)
        os.remove(file_name)

@app.on_callback_query(filters.regex(r'^audio$'))
async def handle_audio_selection(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    logging.debug("Audio option selected")

    url = url_list.get(user_id)
    if not url:
        await callback_query.answer("URL not found.")
        return

    cache_key = (url, 'audio')
    if cache_key in cache:
        await callback_query.answer("Sending cached audio...")
        cached_message_id = cache[cache_key]
        await app.forward_messages(
            chat_id=callback_query.message.chat.id, 
            from_chat_id=cached_message_id[0], 
            message_ids=cached_message_id[1],
            drop_author=True
        )
    else:
        await callback_query.answer("Audio option selected")
        file_name = await download_audio(url)
        logging.debug(f"Downloaded file: {file_name}")
        sent_message = await app.send_audio(
            chat_id=callback_query.message.chat.id, 
            audio=file_name, 
            caption="audio"
        )
        cache[cache_key] = (callback_query.message.chat.id, sent_message.id)
        os.remove(file_name)

def run_bot():
    logging.info("Запуск бота...")
    app.run()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

