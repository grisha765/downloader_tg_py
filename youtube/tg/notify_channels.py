import asyncio
from db.channel import get_all_channels
from youtube.scrap import main as scrap_video_url
from youtube.download import get_video_info
from youtube.tg.video import download_video_tg
from config import logging_config
logging = logging_config.setup_logging(__name__)

last_sent_urls = {}
async def process_user_channels(app):
    for user_id, channel_urls in await get_all_channels():
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
