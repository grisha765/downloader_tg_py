import asyncio, os, glob
from youtube.hooks import ProgressHook, update_progress
from db.cache import get_cache, set_cache
from youtube.download import download_audio
from config import logging_config
logging = logging_config.setup_logging(__name__)

async def download_audio_tg(app, url, quality, message, user_id):
    progress_hook = ProgressHook()
    chat_id, message_id = await get_cache(url, quality)
    if chat_id is not None and message_id is not None:
        logging.debug(f"Cache find, forward message: {chat_id, message_id}")
        await app.forward_messages(
            chat_id=message.chat.id, 
            from_chat_id=chat_id, 
            message_ids=message_id,
            drop_author=True
        )
    else:
        info_message = await message.reply_text(f"🟥Download audio...\n🟥Send audio to telegram...")
        progress_task = asyncio.create_task(update_progress(info_message, progress_hook, "audio"))
        file_name = await download_audio(url, progress_hook)
        logging.debug(f"{user_id}: Downloaded file: {file_name}")
        progress_task.cancel()
        await info_message.edit_text(f"✅Download audio: 100%\n🟥Send audio to telegram...")
        sent_message = await app.send_audio(
            chat_id=message.chat.id, 
            audio=file_name, 
            caption=f"{file_name}"
        )
        await info_message.edit_text(f"✅Download audio: 100%\n✅Send audio to telegram...")
        log_message = await set_cache(url, quality, message.chat.id, sent_message.id)
        logging.debug(f"{log_message}")
        pattern = file_name.replace(".mp3", "*")
        files_to_delete = glob.glob(pattern)
        for file in files_to_delete:
            os.remove(file)
            logging.debug(f"{user_id}: File deleted: {file}")
