import asyncio
from bot.youtube.downloader import download_media, download_thumbnail
from bot.youtube.sponsorblock import sponsorblock
from bot.db.cache import get_cache, set_cache
from bot.db.cache_qualitys import set_quality_size
from bot.funcs.animations import animate_message
from bot.core.helpers import safe_call
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)

async def download_media_msg(client, message, message_id, url, quality, duration):
    chat_id = message.chat.id
    logging.debug(f"Found URL: {url} - Quality: {quality}")
    if quality == 2:
        media_name = 'audio'
    else:
        media_name = 'video'

    cached_chat_id, cached_message_id = await get_cache(url, int(quality))
    if cached_chat_id and cached_message_id:
        logging.debug(f"Cache find, forward message: {cached_chat_id, cached_message_id}")
        await safe_call(
            client.forward_messages,
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
            base_text=f"Preparing your {media_name} download...",
            started_event=download_started_event,
            refresh_rate=1.0
        )
    )

    try:
        media = await download_media(
            url,
            int(quality),
            client,
            chat_id,
            message_id,
            download_started_event
        )
    except Exception as e:
        logging.error(f"Downloading error: {e}")
        media = False

    spinner_task.cancel()

    if not media:
        await safe_call(
            message.edit_text,
            text=f"Error downloading the {media_name}."
        )
        return

    upload_started_event = asyncio.Event()
    upload_spinner_task = asyncio.create_task(
        animate_message(
            message=message,
            base_text=f"Download complete! Uploading {media_name}...",
            started_event=upload_started_event,
            refresh_rate=1.0
        )
    )

    try:
        msg = f"URL: {url}\nQuality: {'audio' if quality == 2 else quality}\n"
        msg = msg + await sponsorblock(url)
        thumbnail = await download_thumbnail(client, message.photo.file_id)
    except Exception as e:
        logging.error(f"Uploading error: {e}")
        msg = False
        thumbnail = False

    if not msg or not thumbnail:
        upload_spinner_task.cancel()
        await safe_call(
            message.edit_text,
            text=f"Error Uploading the {media_name}."
        )
        return

    if quality == 2:
        media_msg = await safe_call(
            message.reply_audio,
            media,
            thumb=thumbnail,
            caption=msg
        )
    else:
        media_msg = await safe_call(
            message.reply_video,
            media,
            thumb=thumbnail,
            duration=duration,
            caption=msg
        )

    upload_spinner_task.cancel()

    await set_cache(url, int(quality), media_msg.chat.id, media_msg.id)

    size_in_bytes = len(media.getvalue())
    size_in_mb = round(size_in_bytes / (1024 * 1024), 2)
    await set_quality_size(url, int(quality), size_in_mb)

    await message.delete()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

