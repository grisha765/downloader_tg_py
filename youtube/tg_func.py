import re, os, tempfile, asyncio, glob
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from youtube.download import download_audio, download_video, get_video_info
from youtube.hooks import ProgressHook, update_progress
from youtube.scrap import main as scrap_video_url
from config import logging_config
logging = logging_config.setup_logging(__name__)

url_list = {}
last_sent_urls = {}

cache = {}
user_options = {}
user_channels = {}

def add_channel(user_id, url):
    if user_id in user_channels:
        user_channels[user_id].append(url)
    else:
        user_channels[user_id] = [url]

def get_channels(user_id):
    return user_channels.get(user_id, [])

def del_channel(user_id, url):
    if user_id in user_channels:
        if url in user_channels[user_id]:
            user_channels[user_id].remove(url)
            if not user_channels[user_id]:
                del user_channels[user_id]
            return True
        else:
            return False
    else:
        return False

def toggle_user_option(user_id, option_name):
    if user_id not in user_options:
        user_options[user_id] = {}
    if option_name not in user_options[user_id]:
        user_options[user_id][option_name] = False
    user_options[user_id][option_name] = not user_options[user_id][option_name]

def get_user_option(user_id, option_name):
    if user_id in user_options and option_name in user_options[user_id]:
        return user_options[user_id][option_name]
    else:
        return False

def create_quality_buttons(qualities):
    buttons = []
    for quality in qualities:
        quality_number = re.match(r'(\d+)', quality).group(1)
        buttons.append([InlineKeyboardButton(quality, callback_data=f'quality_{quality_number}')])
    buttons.append([InlineKeyboardButton("Audio", callback_data='audio')])
    return InlineKeyboardMarkup(buttons)

async def sponsor_block_toggle(message):
    user_id = message.from_user.id
    option_name = 'sponsor'
    toggle_user_option(user_id, option_name)
    logging.debug(f"{user_id}: Option '{option_name}' toggled to {get_user_option(user_id, option_name)}.")
    await message.reply_text(f"Option '{option_name}' toggled to {get_user_option(user_id, option_name)}.")

async def add_channel_command(message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        await message.reply_text("Please provide the channel URL.")
        return

    url = message.command[1]
    add_channel(user_id, url)
    logging.debug(f"{user_id}: A channel with URL {url} has been added to the database. {user_channels}")
    await message.reply_text(f"A channel with URL {url} has been added to the database.\n{get_channels(user_id)}")

async def del_channel_command(message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        await message.reply_text("Please provide the channel URL.")
        return

    url = message.command[1]
    del_channel(user_id, url)
    logging.debug(f"{user_id}: A channel with URL {url} has been deleted from database. {user_channels}")
    await message.reply_text(f"A channel with URL {url} has been deleted from database.\n{get_channels(user_id)}")

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
                await message.reply_photo(photo=video_info['thumbnail'], caption=message_text, reply_markup=reply_markup)
                await info_message.delete()
    else:
        logging.debug(f"{user_id}: No URLs found in the message.")

async def download_video_tg(app, url, quality, message, user_id):
    progress_hook = ProgressHook()
    cache_key = (url, quality)
    if cache_key in cache:
        cached_message_id = cache[cache_key]
        await app.forward_messages(
            chat_id=message.chat.id, 
            from_chat_id=cached_message_id[0], 
            message_ids=cached_message_id[1],
            drop_author=True
        )
    else:
        info_message = await message.reply_text(f"🟥Download video...\n🟥Send video to telegram...")
        progress_task = asyncio.create_task(update_progress(info_message, progress_hook, "video"))
        file_name = await download_video(url, quality, progress_hook, get_user_option(user_id, 'sponsor'))
        logging.debug(f"{user_id}: Downloaded file: {file_name}")
        progress_task.cancel()
        await info_message.edit_text(f"✅Download video: 100%\n🟥Send video to telegram...")
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_thumb:
            thumb_file_id = message.photo.file_id
            await app.download_media(thumb_file_id, file_name=temp_thumb.name)
            sent_message = await app.send_video(
                chat_id=message.chat.id, 
                video=file_name,
                thumb=temp_thumb.name,
                caption=f"{file_name}"
            )
        await info_message.edit_text(f"✅Download video: 100%\n✅Send video to telegram...")
        cache[cache_key] = (message.chat.id, sent_message.id)
        pattern = file_name.replace(".mp4", "*")
        files_to_delete = glob.glob(pattern)
        for file in files_to_delete:
            os.remove(file)
            logging.debug(f"{user_id}: File deleted: {file}")

async def func_video_selection(callback_query: CallbackQuery, app):
    quality = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id
    
    logging.debug(f"{user_id}: Selected quality: {quality}")

    url = url_list.get(user_id)
    if not url:
        await callback_query.answer("URL not found.")
        return
    await download_video_tg(app, url, quality, callback_query.message, user_id)

async def process_user_channels(app):
    for user_id, channel_urls in user_channels.items():
        if user_id not in last_sent_urls:
            last_sent_urls[user_id] = {}
        for channel_url in channel_urls:
            new_video_url = await scrap_video_url(channel_url)
            if new_video_url:
                if last_sent_urls[user_id].get(channel_url) != new_video_url:
                    logging.debug(f"{user_id}: New video found on {channel_url}: {new_video_url}")
                    video_info = await get_video_info(new_video_url)
                    message_text = f"""
**Название**: {video_info['name']}
**Автор**: {video_info['author']}
**Дата выхода**: {video_info['date']}
**Продолжительность**: {video_info['duration']}
**Ссылка**: {new_video_url}
                """
                    message = await app.send_photo(user_id, video_info['thumbnail'], caption=message_text)
                    await download_video_tg(app, new_video_url, '720', message, user_id)
                    last_sent_urls[user_id][channel_url] = new_video_url
                else:
                    logging.debug(f"User {user_id} already received the latest video from {channel_url}.")
            else:
                logging.debug(f"No new video found for channel {channel_url}.")
        await asyncio.sleep(1)

async def func_audio_selection(callback_query: CallbackQuery, app):
    user_id = callback_query.from_user.id
    progress_hook = ProgressHook()
    logging.debug(f"{user_id}: Audio option selected")

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
        logging.debug(f"{user_id}: Downloaded file: {file_name}")
        progress_task.cancel()
        await info_message.edit_text(f"✅Download audio: 100%\n🟥Send audio to telegram...")
        sent_message = await app.send_audio(
            chat_id=callback_query.message.chat.id, 
            audio=file_name, 
            caption=f"{file_name}"
        )
        await info_message.edit_text(f"✅Download audio: 100%\n✅Send audio to telegram...")
        cache[cache_key] = (callback_query.message.chat.id, sent_message.id)
        pattern = file_name.replace(".mp3", "*")
        files_to_delete = glob.glob(pattern)
        for file in files_to_delete:
            os.remove(file)
            logging.debug(f"{user_id}: File deleted: {file}")

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
