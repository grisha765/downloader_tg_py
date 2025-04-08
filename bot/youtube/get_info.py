import asyncio
from typing import Any, Dict
from bot.core.classes import Common
from bot.db.cache_qualitys import set_qualitys, get_qualitys
from bot.config.config import Config
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)

async def get_video_info(url: str) -> dict:
    output = await get_qualitys(url)
    if output:
        logging.debug("Use video info from cache")
        return output

    loop = asyncio.get_event_loop()

    def _format(_url: str, fmt: str):
        ydl_opts = {
            'quiet': True,
            'noplaylist': True,
            'format': fmt,
            'simulate': False,
        }
        if Config.http_proxy:
            ydl_opts['proxy'] = Config.http_proxy

        with Common.youtube(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(_url, download=False)
            except Exception as e:
                logging.error(f'Extract video error: {e}')
                return None

        if not info or "requested_formats" not in info:
            return None

        total_bytes = 0
        for f in info["requested_formats"]:
            total_bytes += (f.get('filesize') or f.get('filesize_approx') or 0)
        return total_bytes if total_bytes > 0 else None

    def _get_video_info_sync(_url: str) -> dict:
        base_opts: Dict[str, Any] = {
            'quiet': True,
            'noplaylist': True,
        }
        if Config.http_proxy:
            base_opts['proxy'] = Config.http_proxy

        with Common.youtube(base_opts) as ydl:
            info = ydl.extract_info(_url, download=False)
        if not info or "formats" not in info:
            return {}

        native_mp4_available = any(
            (f.get('ext') == 'mp4' and f.get('vcodec') != 'none')
            for f in info['formats']
        )

        all_heights = sorted({
            f['height']
            for f in info['formats']
            if (f.get('height') and f.get('vcodec') != 'none')
        })

        result = {}

        for quality in all_heights:
            if native_mp4_available:
                logging.debug(f"Use mp4 for quality: {quality}")
                format_str = f"bestvideo[ext=mp4][height={quality}]+bestaudio[ext=m4a]/mp4"
            else:
                format_str = f"bestvideo[height={quality}]+bestaudio/best"

            total_bytes = _format(_url, format_str)
            if total_bytes:
                result[quality] = round(total_bytes / (1024 * 1024), 2)

        return result

    output = await loop.run_in_executor(None, _get_video_info_sync, url)
    await set_qualitys(url, output)

    return output

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
