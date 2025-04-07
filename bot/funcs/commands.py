import re, pyrogram.types
from bot.funcs.youtube import download_video, get_video_info
from bot.core.classes import Common
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
        try:
            quality_dict = await get_video_info(url_message)
        except Exception as e:
            message.reply(f"Error retrieving video info: {e}")
            return

        buttons = []
        for quality, size in quality_dict.items():
            button_text = f"{quality}p - {size} MB"
            button = pyrogram.types.InlineKeyboardButton(text=button_text, callback_data=f"quality_{quality}")
            buttons.append([button])

        reply_markup = pyrogram.types.InlineKeyboardMarkup(buttons)

        await message.reply("Select video quality:", reply_markup=reply_markup)


async def download_video_command(client, callback_query):
    quality = callback_query.data.split("_", 1)[1]
    message = callback_query.message
    message_id = message.id
    chat_id = message.chat.id
    url_message = Common.select_video.get(message_id)
    assert url_message, "No URL found for this message ID"

    await callback_query.answer(f"You selected {quality}p quality!")
    await message.edit_text("Preparing your video download...")

    logging.debug(f"Found URL: {url_message} - Quality: {quality}")

    video = await download_video(url_message, quality, client, chat_id, message_id)
    await message.edit_text("Download complete! Uploading video...")
    await message.reply_video(video, caption="Here is your video!")

    Common.select_video.pop(message_id, None)
    await message.delete()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

