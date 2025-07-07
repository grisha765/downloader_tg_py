import re, pyrogram.types, asyncio
from bot.funcs.animations import animate_message
from bot.funcs.options import options_menu, option_set, quality_menu, refresh_menu
from bot.funcs.media_msg import download_media_msg
from bot.funcs.watchdog import watchdog_switch
from bot.youtube.get_info import get_video_metainfo, get_video_info
from bot.db.cache import get_cache
from bot.db.channels import get_channels, add_channel, del_channel
from bot.core.helpers import safe_call, Common
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)


async def start_command(_, message):
    await message.reply_text(
        "Welcome! To download a YouTube video directly to Telegram, simply send the video URL to this bot.\n\n"
        "- Use `/menu` to open a menu of additional functions and bot settings.\n"
        "- Use `/channel` to manage and add channels to the watch list.\n\n"
        "Enjoy using the bot!"
    )


async def get_video_command(_, message):
    text = message.text
    user_id = message.from_user.id
    chat_id = message.chat.id
    sem = Common.user_semaphores[chat_id]
    if sem.locked() and sem._value == 0:
        await safe_call(
            message.reply,
            text="You can't download more than 5 videos."
        )
        return

    logging.debug(f"{user_id}: Received message: {text}")
    url_pattern = r'(https?://(?:www\.|m\.)?youtube\.com/(?:watch\?v=|shorts/)[\w-]+|https?://youtu\.be/[\w-]+)'
    url_message = "".join(re.findall(url_pattern, text))
    
    if url_message:
        await sem.acquire()
        Common.select_video.setdefault(chat_id, {})
        msg_info = await safe_call(
            message.reply,
            text="Retrieving video info..."
        )
        spinner_event = asyncio.Event()
        spinner_task = asyncio.create_task(
            animate_message(
                message=msg_info,
                base_text="Retrieving video info...",
                started_event=spinner_event,
                refresh_rate=1.0
            )
        )
        
        try:
            quality_dict = await get_video_metainfo(url_message)
            logging.debug(f"Available qualitys: {quality_dict}")
            video_info = await get_video_info(url_message)
        except Exception as e:
            logging.error(f"Error retrieving video info: {e}")
            quality_dict = False
            video_info = False

        spinner_task.cancel()

        if not quality_dict or not video_info:
            await safe_call(
                msg_info.edit_text,
                text="Error retrieving video info."
            )
            return

        msg_text = (
            f"**Name**: {video_info['name']}\n"
            f"**Author**: {video_info['author']}\n"
            f"**Release date**: {video_info['date']}\n"
            f"**Duration**: {video_info['duration']}\n"
            f"**URL Link**: {url_message}"
        )

        buttons = []
        for quality, size in quality_dict.items():
            cached_chat_id, cached_message_id = await get_cache(url_message, int(quality))
            
            if cached_chat_id and cached_message_id:
                color_emoji = "🟢"
            else:
                color_emoji = "🔴"

            if quality == 2:
                button_text = f"{color_emoji} AUDIO - {size} MB"
            else:
                button_text = f"{color_emoji} {quality}p - {size} MB"

            if float(size) > 2000.00:
                quality = 0
            button = pyrogram.types.InlineKeyboardButton(
                text=button_text, 
                callback_data=f"quality_{quality}"
            )
            buttons.append([button])

        cancel_button = pyrogram.types.InlineKeyboardButton(
            text='🗑Cancel 🗑',
            callback_data=f'quality_1'
        )
        buttons.append([cancel_button])

        reply_markup = pyrogram.types.InlineKeyboardMarkup(buttons)

        msg = await safe_call(
            message.reply_photo,
            photo=video_info['thumbnail'],
            caption=msg_text,
            reply_markup=reply_markup
        )
        Common.select_video[chat_id][msg.id] = {
            "url": url_message,
            "duration": video_info['duration_sec'],
            "sem": sem
        }

        await msg_info.delete()


async def download_video_command(client, callback_query):
    quality = int(callback_query.data.split("_", 1)[1])
    message = callback_query.message
    message_id = message.id
    chat_id = message.chat.id
    entry = Common.select_video[chat_id].get(message_id)
    sem = entry.pop('sem')
    if sem is None:
        await callback_query.answer(
            'The download has already started.'
        )
        return
    match quality:
        case 0:
            await callback_query.answer(
                'This file exceeds 2GB and cannot be downloaded.',
                show_alert=True
            )
            return
        case 1:
            await callback_query.answer(
                'Download canceled.'
            )
            await message.delete()
            Common.select_video[chat_id].pop(message_id, None)
            sem.release()
            return

    url_message = entry['url']
    duration = entry['duration']

    if quality == 2:
        await callback_query.answer("You selected audio download!")
    else:
        await callback_query.answer(f"You selected {quality}p quality!")

    try:
        await download_media_msg(client, message, message_id, url_message, quality, duration)
    finally:
        Common.select_video[chat_id].pop(message_id, None)
        sem.release()


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
        await safe_call(
            message.reply_text,
            text=(
                "**Usage**: `/channel` command `@channel_name`\n"
                "**Commands**:\n"
                "  `add` - add a channel to the watch list.\n"
                "  `del` - remove a channel from the test list.\n"
                "  `list` - view all channels."
            )
        )
        return
    command = message.command[1]
    if len(message.command) < 3 and not command == 'list':
        await safe_call(
            message.reply_text,
            text="Please provide the channel URL."
        )
        return

    if command != 'list':
        channelname = message.command[2]
        if isinstance(channelname, str) and re.fullmatch(r'@[\w\.-]+', channelname):
            url_message = f'https://www.youtube.com/{channelname}/videos'
        else:
            await safe_call(
                message.reply_text,
                text='Error in channel username format, example: @channel_name'
            )
            return
    else:
        url_message = ''

    match command:
        case "add":
            if url_message:
                info_message = await add_channel(user_id, url_message)
                if not info_message:
                    await safe_call(
                        message.reply_text,
                        text=(
                            "Channel has not been added to the database"
                            "perhaps such a channel already exists."
                        )
                    )
                    return
                logging.debug(f"{user_id}: Has been added channel: {url_message}")
                await safe_call(
                    message.reply_text,
                    text=f"A channel with URL {url_message} has been added to the database."
                )
        case "del":
            if url_message:
                info_message = await del_channel(user_id, url_message)
                if not info_message:
                    await safe_call(
                        message.reply_text,
                        text=(
                            "The channel has not been deleted from the database"
                            "perhaps this channel does not exist."
                        )
                    )
                    return
                logging.debug(f"{user_id}: Has been deleted channel: {url_message}")
                await safe_call(
                    message.reply_text,
                    text=f"A channel with URL {url_message} has been deleted from database."
                )
        case "list":
            channels = await get_channels(user_id)
            channels_str = "\n".join(f"{i+1}. {url}" for i, url in enumerate(channels))
            await safe_call(
                message.reply_text,
                text=f"Channels:\n{channels_str}",
                disable_web_page_preview=True
            )

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

