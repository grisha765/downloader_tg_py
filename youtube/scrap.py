import yt_dlp
import asyncio
from config import logging_config
logging = logging_config.setup_logging(__name__)

async def main(channel_url):
    ydl_opts = {
        'extract_flat': True,
        'playlistend': 1,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = await asyncio.to_thread(ydl.extract_info, channel_url, download=False)

    if 'entries' in result and len(result['entries']) > 0:
        latest_video = result['entries'][0]
        logging.debug(f"Title: {latest_video['title']}, URL: https://www.youtube.com/watch?v={latest_video['id']}")
        return latest_video['id']
    else:
        print("No videos found.")
        return None

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

