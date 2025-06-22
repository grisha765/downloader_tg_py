import asyncio
from typing import Any, Dict, Union
from bot.core.classes import Common
from bot.db.cache_qualitys import set_qualitys, get_qualitys
from bot.config.config import Config
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)

async def get_video_metainfo(url: str) -> dict:
    output = await get_qualitys(url)
    if output:
        logging.debug("Use video metainfo from cache")
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
            logging.debug("Use http proxy")
        if Config.cookie_path:
            ydl_opts['cookiefile'] = Config.cookie_path
            logging.debug("Use cookie file")

        with Common.youtube(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(_url, download=False)
            except Exception as e:
                logging.error(f'Extract video error: {e}')
                return None

        if not info:
            return None

        if "requested_formats" not in info:
            single_bytes = info.get('filesize') or info.get('filesize_approx')
            return single_bytes if single_bytes else None

        total_bytes = 0
        for f in info["requested_formats"]:
            total_bytes += (f.get('filesize') or f.get('filesize_approx') or 0)
        return total_bytes if total_bytes > 0 else None

    def _get_video_metainfo_sync(_url: str) -> dict:
        base_opts: Dict[str, Any] = {
            'quiet': True,
            'noplaylist': True,
        }
        if Config.http_proxy:
            base_opts['proxy'] = Config.http_proxy
            logging.debug("Use http proxy")
        if Config.cookie_path:
            base_opts['cookiefile'] = Config.cookie_path
            logging.debug("Use cookie file")

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

        audio_size = _format(_url, "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio")
        if audio_size:
            result[2] = round(audio_size / (1024 * 1024), 2)

        return result

    output = await loop.run_in_executor(None, _get_video_metainfo_sync, url)
    await set_qualitys(url, output)

    return output

async def get_video_info(url: str) -> Dict[str, Union[str, int, None]]:
    loop = asyncio.get_event_loop()

    def _get_video_info_sync(_url: str):
        ydl_opts: Dict[str, Any] = {
            'quiet': True,
            'noplaylist': True,
        }
        if Config.http_proxy:
            ydl_opts['proxy'] = Config.http_proxy
            logging.debug("Use http proxy")
        if Config.cookie_path:
            ydl_opts['cookiefile'] = Config.cookie_path
            logging.debug("Use cookie file")

        with Common.youtube(ydl_opts) as ydl:
            info = ydl.extract_info(_url, download=False)
        if not info:
            logging.error(f"Failed to retrieve channel information from the link: {_url}")
            return {}
        name = info.get('title', 'N/A')
        duration = info.get('duration', 'N/A')
        duration_sec = duration if duration != 'N/A' else 0
        upload_date = info.get('upload_date', 'N/A')
        author = info.get('uploader', 'N/A')

        thumbnail = None
        thumbs = info.get("thumbnails") or []
        for t in reversed(thumbs):
            url = t.get("url", '')
            clean_url = url.split("?", 1)[0].lower()
            if clean_url.lower().endswith((".jpg", ".jpeg", ".png")):
                thumbnail = url
                break
        if not thumbnail:
            raw_thumb = info.get("thumbnail")
            if raw_thumb:
                fixed = raw_thumb.replace("/vi_webp/", "/vi/")
                if fixed.lower().endswith(".webp"):
                    fixed = fixed[:-5] + ".jpg"
                thumbnail = fixed

        if duration != 'N/A':
            if duration < 60:
                duration_str = f"{duration} seconds"
            elif duration < 3600:
                minutes, seconds = divmod(duration, 60)
                duration_str = f"{minutes} minutes {seconds} seconds"
            else:
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)
                duration_str = f"{hours} hours {minutes} minutes {seconds} seconds"
        else:
            duration_str = 'Unknown duration'
        
        video_info = {
            "name": name,
            "duration": duration_str,
            "duration_sec": duration_sec,
            "date": upload_date if upload_date != 'N/A' else 'Unknown date',
            "author": author if author != 'N/A' else 'Unknown author',
            "thumbnail": thumbnail,
        }
        return video_info

    output = await loop.run_in_executor(None, _get_video_info_sync, url)

    return output


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
