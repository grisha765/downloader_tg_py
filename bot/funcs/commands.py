import re, pyrogram.types, asyncio
from bot.funcs.animations import animate_message
from bot.funcs.options import options_menu, option_set, quality_menu, refresh_menu, watchdog_switch
from bot.funcs.video_msg import download_video_msg
from bot.youtube.get_info import get_video_info
from bot.db.cache import get_cache
from bot.db.channels import get_channels, add_channel, del_channel
from bot.core.classes import Common
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)


async def start_command(_, message):
    await message.reply_text("Hello world.")


async def get_video_command(_, message):
    text = message.text
    message_id = message.id
    user_id = message.from_user.id
    chat_id = message.chat.id

    logging.debug(f"{user_id}: Received message: {text}")
    url_pattern = r'(https?://(?:www\.|m\.)?youtube\.com/watch\?v=[\w-]+|https?://youtu\.be/[\w-]+)'
    url_message = "".join(re.findall(url_pattern, text))
    
    if url_message:
        Common.select_video[chat_id] = {message_id + 1: url_message}

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
            logging.debug(f"Available qualitys: {quality_dict}")
        except Exception as e:
            logging.error(f"Error retrieving video info: {e}")
            quality_dict = False

        spinner_task.cancel()

        if not quality_dict:
            await msg.edit_text("Error retrieving video info.")
            return

        buttons = []
        for quality, size in quality_dict.items():
            cached_chat_id, cached_message_id = await get_cache(url_message, int(quality))
            
            if cached_chat_id and cached_message_id:
                color_emoji = "🟢"
            else:
                color_emoji = "🔴"

            button_text = f"{color_emoji} {quality}p - {size} MB"
            if float(size) > 2000.00:
                quality = 'large'
            button = pyrogram.types.InlineKeyboardButton(
                text=button_text, 
                callback_data=f"quality_{quality}"
            )
            buttons.append([button])

        reply_markup = pyrogram.types.InlineKeyboardMarkup(buttons)

        await msg.edit_text("Select video quality:", reply_markup=reply_markup)


async def download_video_command(client, callback_query):
    quality = callback_query.data.split("_", 1)[1]
    if quality == 'large':
        await callback_query.answer(
            'This file exceeds 2GB and cannot be downloaded.',
            show_alert=True
        )
        return

    message = callback_query.message
    message_id = message.id
    chat_id = message.chat.id
    url_message = Common.select_video[chat_id].get(message_id)
    if not url_message:
        logging.error("No URL found for this message ID")
        await callback_query.answer()
        return
    await callback_query.answer(f"You selected {quality}p quality!")

    await download_video_msg(client, message, message_id, url_message, quality)

    Common.select_video[chat_id].pop(message_id, None)


async def options_command(_, message):
    await options_menu(message)


async def options_buttons(client, callback_query):
    data = callback_query.data.split("_", 1)[1]
    match data:
        case 'quality':
            await quality_menu(callback_query)
        case 'refresh':
            await refresh_menu(callback_query)
        case 'back':
            await options_menu(callback_query)
        case 'watchdog':
            await watchdog_switch(client, callback_query)

async def options_set_buttons(_, callback_query):
    data = callback_query.data.split("_")
    await option_set(callback_query, data[2], data[3])


async def channel_command(_, message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        await message.reply_text(
            "**Usage**: /channel <command> <url>\n"
            "**Commands**:\n"
            "  add - add a channel to the watch list.\n"
            "  del - remove a channel from the test list.\n"
            "  list - view all channels."
        )
        return
    command = message.command[1]
    if len(message.command) < 3 and not command == 'list':
        await message.reply_text("Please provide the channel URL.")
        return

    match command:
        case "add":
            url = message.command[2]
            info_message = await add_channel(user_id, url)
            if not info_message:
                await message.reply_text(
                    "Channel has not been added to the database"
                    "perhaps such a channel already exists."
                )
                return
            logging.debug(f"{user_id}: Has been added channel: {url}")
            await message.reply_text(f"A channel with URL {url} has been added to the database.")
        case "del":
            url = message.command[2]
            info_message = await del_channel(user_id, url)
            if not info_message:
                await message.reply_text(
                    "The channel has not been deleted from the database"
                    "perhaps this channel does not exist."
                )
                return
            logging.debug(f"{user_id}: Has been deleted channel: {url}")
            await message.reply_text(f"A channel with URL {url} has been deleted from database.")
        case "list":
            channels = await get_channels(user_id)
            channels_str = "\n".join(f"{i+1}. {url}" for i, url in enumerate(channels))
            await message.reply_text(
                f"Channels:\n{channels_str}",
                disable_web_page_preview=True
            )


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

