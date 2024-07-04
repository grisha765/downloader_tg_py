import aiohttp
import re
from config import logging_config
logging = logging_config.setup_logging(__name__)

async def fetch_html(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main(channel):
    async with aiohttp.ClientSession() as session:
        html = await fetch_html(session, channel + "/videos")
        
        info = re.search(r'(?<={"label":").*?(?="})', html).group()
        video_id = re.search(r'(?<="videoId":").*?(?=")', html).group()
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        logging.debug(f'Video info: {info}')
        logging.debug(f'Video url: {url}')
        return url

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
