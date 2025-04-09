import asyncio
from bot.core.classes import Common
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)

async def channel_scrap(channel_url: str) -> str:
    loop = asyncio.get_event_loop()

    def _get_channel_info(_url: str):
        ydl_opts = {
            'extract_flat': True,
            'playlistend': 1,
        }

        with Common.youtube(ydl_opts) as ydl:
            info = ydl.extract_info(_url, download=False)
        if not info:
            raise ValueError(f"Failed to retrieve channel information from the link: {_url}")

        if 'entries' in info and len(info['entries']) > 0:
            latest_video = info['entries'][0]
            url = f"https://www.youtube.com/watch?v={latest_video['id']}" 
            logging.debug(f"Title: {latest_video['title']}, URL: {url}")
            return url
        else:
            return ''

    output = await loop.run_in_executor(None, _get_channel_info, channel_url)
    return output

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

