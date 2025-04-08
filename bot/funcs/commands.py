import re, pyrogram.types, asyncio
from bot.funcs.animations import animate_message
from bot.youtube.downloader import download_video
from bot.funcs.options import options_menu, option_set, quality_menu, refresh_menu
from bot.youtube.get_info import get_video_info
from bot.youtube.sponsorblock import sponsorblock
from bot.core.classes import Common
from bot.db.cache import get_cache, set_cache
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)


async def start_command(_, message):
    await message.reply_text("Hello world.")


async def get_video_command(_, message):
    text = message.text
    message_id = message.id
    user_id = message.from_user.id

    logging.debug(f"{user_id}: Received message: {text}")
    url_pattern = r'(https?://(?:www\.|m\.)?youtube\.com/watch\?v=[\w-]+|https?://youtu\.be/[\w-]+)'
    url_message = "".join(re.findall(url_pattern, text))
    
    if url_message:
        Common.select_video[message_id + 1] = url_message

        msg = await message.reply("Retrieving video info...")
        spinner_event = asyncio.Event()
        spinner_task = asyncio.create_task(
            animate_message(
                message=msg,
                base_text="Retrieving video info...",
                started_event=spinner_event,
                refresh_rate=1.0
            )
        )
        
        try:
            quality_dict = await get_video_info(url_message)
        except Exception as e:
            spinner_task.cancel()
            try:
                await spinner_task
            except asyncio.CancelledError:
                pass
            msg.edit_text(f"Error retrieving video info: {e}")
            return

        spinner_task.cancel()
        try:
            await spinner_task
        except asyncio.CancelledError:
            pass

        buttons = []
        for quality, size in quality_dict.items():
            cached_chat_id, cached_message_id = await get_cache(url_message, int(quality))
            
            if cached_chat_id and cached_message_id:
                color_emoji = "🟢"
            else:
                color_emoji = "🔴"

            button_text = f"{color_emoji} {quality}p - {size} MB"
            button = pyrogram.types.InlineKeyboardButton(
                text=button_text, 
                callback_data=f"quality_{quality}"
            )
            buttons.append([button])

        reply_markup = pyrogram.types.InlineKeyboardMarkup(buttons)

        await msg.edit_text("Select video quality:", reply_markup=reply_markup)


async def download_video_command(client, callback_query):
    quality = callback_query.data.split("_", 1)[1]
    message = callback_query.message
    message_id = message.id
    chat_id = message.chat.id
    url_message = Common.select_video.get(message_id)
    assert url_message, "No URL found for this message ID"

    await callback_query.answer(f"You selected {quality}p quality!")

    logging.debug(f"Found URL: {url_message} - Quality: {quality}")

    cached_chat_id, cached_message_id = await get_cache(url_message, int(quality))
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
            url_message,
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

    msg = await sponsorblock(url_message)
    video_msg = await message.reply_video(video, caption=msg)

    upload_spinner_task.cancel()
    try:
        await upload_spinner_task
    except asyncio.CancelledError:
        pass

    await set_cache(url_message, int(quality), video_msg.chat.id, video_msg.id)

    Common.select_video.pop(message_id, None)
    await message.delete()


async def options_command(_, message):
    await options_menu(message)


async def options_buttons(_, callback_query):
    data = callback_query.data.split("_", 1)[1]
    match data:
        case 'quality':
            await quality_menu(callback_query)
        case 'refresh':
            await refresh_menu(callback_query)
        case 'back':
            await options_menu(callback_query)

async def options_set_buttons(_, callback_query):
    data = callback_query.data.split("_")
    await option_set(callback_query, data[2], data[3])

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

