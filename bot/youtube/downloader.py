import tempfile, asyncio
from pathlib import Path
from io import BytesIO
from typing import Any, Dict
from bot.youtube.hooks import create_progress_hook
from bot.core.classes import Common
from bot.config.config import Config
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)

async def download_media(url: str, quality: int, app, chat_id: int, message_id: int, download_started_event: asyncio.Event):
    loop = asyncio.get_event_loop()

    def _download_media_sync(_url: str, _quality: int):
        progress_hook = create_progress_hook(app, chat_id, message_id, loop, download_started_event)

        info_opts: Dict[str, Any] = {
            'quiet': True,
            'noplaylist': True,
        }
        if Config.http_proxy:
            info_opts['proxy'] = Config.http_proxy
            logging.debug("Use http proxy")
        if Config.cookie_path:
            info_opts['cookiefile'] = Config.cookie_path
            logging.debug("Use cookie file")

        with Common.youtube(info_opts) as ydl:
            info = ydl.extract_info(_url, download=False)

        native_mp4_available = False
        if not info:
            raise ValueError(f"Failed to retrieve media information from the link: {_url}")
        for fmt in info.get('formats', []):
            ext = fmt.get('ext')
            if ext == 'mp4':
                native_mp4_available = True
                break

        with tempfile.TemporaryDirectory() as tmpdirname:
            logging.debug(f"Temp dir {tmpdirname} available")
            outtmpl = str(Path(tmpdirname) / '%(id)s.%(ext)s')

            ydl_opts = {
                'outtmpl': outtmpl,
                'quiet': True,
                'noplaylist': True,
                'progress_hooks': [progress_hook],
            }
            if _quality == 2:
                ydl_opts['format'] = "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio"
                ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192'
                }]
            else :
                if native_mp4_available:
                    logging.debug("Use mp4 for video")
                    ydl_opts['format'] = f"bestvideo[ext=mp4][height={_quality}]+bestaudio[ext=m4a]/mp4"
                    ydl_opts['postprocessors'] = [{
                            'key': 'FFmpegVideoConvertor',
                            'preferedformat': 'mp4',
                        }]
                else:
                    ydl_opts['format'] = f"bestvideo[height={_quality}]+bestaudio/best"

            if Config.http_proxy:
                ydl_opts['proxy'] = Config.http_proxy
                logging.debug("Use http proxy")
            if Config.cookie_path:
                ydl_opts['cookiefile'] = Config.cookie_path
                logging.debug("Use cookie file")

            with Common.youtube(ydl_opts) as ydl:
                info = ydl.extract_info(_url, download=True)
                filename = ydl.prepare_filename(info)
                if (_quality != 2) and (not native_mp4_available):
                    filename = str(Path(filename).with_suffix('.mp4'))
                if _quality == 2:
                    filename = str(Path(filename).with_suffix('.mp3'))

            with open(filename, 'rb') as f:
                media_bytes = BytesIO(f.read())

            media_bytes.name = Path(filename).name
            media_bytes.seek(0)

        return media_bytes

    return await loop.run_in_executor(None, _download_media_sync, url, quality)


async def download_thumbnail(client, file_id):
    with tempfile.TemporaryDirectory() as tmpdirname:
        logging.debug(f"Temp dir {tmpdirname} available")
        filename = str(Path(tmpdirname) / f'{file_id}.jpg')
        await client.download_media(file_id, file_name=filename)
        with open(filename, 'rb') as f:
            img_bytes = BytesIO(f.read())

        img_bytes.name = Path(filename).name
        img_bytes.seek(0)

        return img_bytes


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
