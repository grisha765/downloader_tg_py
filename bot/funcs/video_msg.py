import asyncio
from bot.youtube.downloader import download_video
from bot.youtube.sponsorblock import sponsorblock
from bot.db.cache import get_cache, set_cache
from bot.db.cache_qualitys import set_quality_size
from bot.funcs.animations import animate_message
from bot.core.classes import Common
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)

async def download_video_msg(client, message, message_id, url, quality):
    chat_id = message.chat.id
    logging.debug(f"Found URL: {url} - Quality: {quality}")

    cached_chat_id, cached_message_id = await get_cache(url, int(quality))
    if cached_chat_id and cached_message_id:
        logging.debug(f"Cache find, forward message: {cached_chat_id, cached_message_id}")
        await client.forward_messages(
            chat_id = chat_id,
            from_chat_id = cached_chat_id,
            message_ids = cached_message_id,
            drop_author=True
        )
        await message.delete()
        return

    download_started_event = asyncio.Event()
    spinner_task = asyncio.create_task(
        animate_message(
            message=message,
            base_text="Preparing your video download...",
            started_event=download_started_event,
            refresh_rate=1.0
        )
    )

    try:
        video = await download_video(
            url,
            quality,
            client,
            chat_id,
            message_id,
            download_started_event
        )
    except Exception as e:
        logging.error(f"Downloading error: {e}")
        video = False

    spinner_task.cancel()
    try:
        await spinner_task
    except asyncio.CancelledError:
        pass

    if not video:
        await message.edit_text("Error downloading the video.")
        return

    upload_started_event = asyncio.Event()
    upload_spinner_task = asyncio.create_task(
        animate_message(
            message=message,
            base_text="Download complete! Uploading video...",
            started_event=upload_started_event,
            refresh_rate=1.0
        )
    )

    msg = await sponsorblock(url)
    video_msg = await message.reply_video(video, caption=msg)

    upload_spinner_task.cancel()
    try:
        await upload_spinner_task
    except asyncio.CancelledError:
        pass

    await set_cache(url, int(quality), video_msg.chat.id, video_msg.id)

    size_in_bytes = len(video.getvalue())
    size_in_mb = round(size_in_bytes / (1024 * 1024), 2)
    await set_quality_size(url, int(quality), size_in_mb)

    Common.select_video.pop(message_id, None)
    await message.delete()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

