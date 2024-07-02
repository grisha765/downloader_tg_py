import re, os, tempfile, asyncio
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from youtube.download import download_audio, download_video, get_video_info
from youtube.hooks import ProgressHook, update_progress
from config import logging_config
logging = logging_config.setup_logging(__name__)

cache = {}
url_list = {}

def create_quality_buttons(qualities):
    buttons = []
    for quality in qualities:
        quality_number = re.match(r'(\d+)', quality).group(1)
        buttons.append([InlineKeyboardButton(quality, callback_data=f'quality_{quality_number}')])
    buttons.append([InlineKeyboardButton("Audio", callback_data='audio')])
    return InlineKeyboardMarkup(buttons)

async def func_message(message):
    text = message.text
    user_id = message.from_user.id
    logging.debug(f"Received message: {text}")

    info_message = await message.reply_text(f"Search video by url...")

    url_pattern = r'(https?://(?:www\.|m\.)?youtube\.com/watch\?v=[\w-]+|https?://youtu\.be/[\w-]+)'
    urls = re.findall(url_pattern, text)
    
    logging.debug(f"Found URLs: {urls}")

    if urls:
        for url in urls:
            url_list[user_id] = url
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
                await info_message.delete()
    else:
        logging.debug("No URLs found in the message.")

async def func_video_selection(callback_query: CallbackQuery, app):
    quality = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    progress_hook = ProgressHook()
    
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
        info_message = await callback_query.message.reply_text(f"🟥Download video...\n🟥Send video to telegram...")
        progress_task = asyncio.create_task(update_progress(info_message, progress_hook, "video"))
        file_name = await download_video(url, quality, progress_hook)
        logging.debug(f"Downloaded file: {file_name}")
        progress_task.cancel()
        await info_message.edit_text(f"✅Download video: 100%\n🟥Send video to telegram...")
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_thumb:
            thumb_file_id = callback_query.message.photo.file_id
            await app.download_media(thumb_file_id, file_name=temp_thumb.name)
            sent_message = await app.send_video(
                chat_id=callback_query.message.chat.id, 
                video=file_name,
                thumb=temp_thumb.name,
                caption=f"{quality}"
            )
        await info_message.edit_text(f"✅Download video: 100%\n✅Send video to telegram...")
        cache[cache_key] = (callback_query.message.chat.id, sent_message.id)
        os.remove(file_name)

async def func_audio_selection(callback_query: CallbackQuery, app):
    user_id = callback_query.from_user.id
    progress_hook = ProgressHook()
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
        info_message = await callback_query.message.reply_text(f"🟥Download audio...\n🟥Send audio to telegram...")
        progress_task = asyncio.create_task(update_progress(info_message, progress_hook, "audio"))
        file_name = await download_audio(url, progress_hook)
        logging.debug(f"Downloaded file: {file_name}")
        progress_task.cancel()
        await info_message.edit_text(f"✅Download audio: 100%\n🟥Send audio to telegram...")
        sent_message = await app.send_audio(
            chat_id=callback_query.message.chat.id, 
            audio=file_name, 
            caption="audio"
        )
        await info_message.edit_text(f"✅Download audio: 100%\n✅Send audio to telegram...")
        cache[cache_key] = (callback_query.message.chat.id, sent_message.id)
        os.remove(file_name)
        
if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
