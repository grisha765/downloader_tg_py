import tempfile, asyncio, os, glob
from youtube.hooks import ProgressHook, update_progress
from db.cache import get_cache, set_cache
from db.option import get_user_option
from youtube.download import download_video
from config import logging_config
logging = logging_config.setup_logging(__name__)

async def download_video_tg(app, url, quality, message, user_id):
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
        info_message = await message.reply_text(f"🟥Download video...\n🟥Send video to telegram...")
        progress_task = asyncio.create_task(update_progress(info_message, progress_hook, "video"))
        file_name = await download_video(url, quality, progress_hook, await get_user_option(user_id, 'sponsor'))
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
        log_message = await set_cache(url, quality, message.chat.id, sent_message.id)
        logging.debug(f"{log_message}")
        pattern = file_name.replace(".mp4", "*")
        files_to_delete = glob.glob(pattern)
        for file in files_to_delete:
            os.remove(file)
            logging.debug(f"{user_id}: File deleted: {file}")
