import re
from bot.funcs.youtube import download_video
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)


async def start_command(_, message):
    await message.reply_text("Hello world.")


async def download_command(_, message):
    text = message.text
    user_id = message.from_user.id

    logging.debug(f"{user_id}: Received message: {text}")
    url_pattern = r'(https?://(?:www\.|m\.)?youtube\.com/watch\?v=[\w-]+|https?://youtu\.be/[\w-]+)'
    url_message = "".join(re.findall(url_pattern, text))
    
    if url_message:
        logging.debug(f"Found URLs: {url_message}")
        video = download_video(url_message)
        await message.reply_video(video, caption="Here is your video!")

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

