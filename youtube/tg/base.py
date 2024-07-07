import re 
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from youtube.download import get_video_info
from youtube.tg.video import download_video_tg
from youtube.tg.audio import download_audio_tg
from config import logging_config
logging = logging_config.setup_logging(__name__)

def create_quality_buttons(qualities):
    buttons = []
    for quality in qualities:
        quality_number = re.match(r'(\d+)', quality).group(1)
        buttons.append([InlineKeyboardButton(quality, callback_data=f'quality_{quality_number}')])
    buttons.append([InlineKeyboardButton("Audio", callback_data='audio')])
    return InlineKeyboardMarkup(buttons)

url_list = {}
async def func_message(message):
    text = message.text
    user_id = message.from_user.id
    logging.debug(f"{user_id}: Received message: {text}")

    url_pattern = r'(https?://(?:www\.|m\.)?youtube\.com/watch\?v=[\w-]+|https?://youtu\.be/[\w-]+)'
    urls = re.findall(url_pattern, text)
    
    logging.debug(f"Found URLs: {urls}")

    if urls:
        info_message = await message.reply_text(f"Search video by url...")
        for url in urls:
            url_list[user_id] = url
            try:
                video_info = await get_video_info(url)
                logging.debug(f"Video info for {url}: {video_info}")
            except:
                await info_message.edit_text("Error retrieving data from url.")
                logging.error(f"{user_id}: Error retrieving data from url: {url}")
                break
            
            qualities = video_info.get('qualities', [])
            if qualities:
                reply_markup = create_quality_buttons(qualities)
                message_text = f"""
**Название**: {video_info['name']}
**Автор**: {video_info['author']}
**Дата выхода**: {video_info['date']}
**Продолжительность**: {video_info['duration']}
                """
                video_info_message = await message.reply_photo(photo=video_info['thumbnail'], caption=message_text, reply_markup=reply_markup)
                await info_message.delete()
                return video_info_message
    else:
        logging.debug(f"{user_id}: No URLs found in the message.")

async def func_video_selection(callback_query: CallbackQuery, app):
    quality = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    
    logging.debug(f"{user_id}: Selected quality: {quality}")

    url = url_list.get(user_id)
    if not url:
        await callback_query.answer("URL not found.")
        return
    await download_video_tg(app, url, quality, callback_query.message, user_id)

async def func_audio_selection(callback_query: CallbackQuery, app):
    user_id = callback_query.from_user.id
    quality = "audio"
    logging.debug(f"{user_id}: Audio option selected")

    url = url_list.get(user_id)
    if not url:
        await callback_query.answer("URL not found.")
        return
    await download_audio_tg(app, url, quality, callback_query.message, user_id)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
