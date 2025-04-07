import yt_dlp, tempfile, asyncio
from pathlib import Path
from io import BytesIO
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)

async def get_video_info(url: str) -> dict:
    loop = asyncio.get_event_loop()

    def _get_video_info_sync(_url: str) -> dict:
        ydl_opts = {
            'quiet': True,
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(_url, download=False)

        quality_size_dict = {}
        assert info
        for fmt in info.get('formats', []):
            height = fmt.get('height')
            if height is None:
                continue
            size = fmt.get('filesize') or fmt.get('filesize_approx')
            if size is None:
                continue
            if height in quality_size_dict:
                quality_size_dict[height] = max(quality_size_dict[height], size)
            else:
                quality_size_dict[height] = size

        quality_size_mb = {
            height: round(size / (1024 * 1024), 2)
            for height, size in quality_size_dict.items()
        }

        sorted_quality_size_mb = dict(sorted(quality_size_mb.items()))
        return sorted_quality_size_mb

    return await loop.run_in_executor(None, _get_video_info_sync, url)


def create_progress_hook(app, chat_id, message_id, loop):
    last_edit_time = 0

    async def _do_edit_message_text(text: str):
        try:
            await app.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text
            )
        except Exception as e:
            logging.warning(f"Failed to edit progress message: {e}")

    def hook(d):
        nonlocal last_edit_time
        if d['status'] == 'downloading':
            downloaded_bytes = d.get('downloaded_bytes', 0)
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            elapsed = d.get('elapsed', 0)
            speed = d.get('speed', 0)

            if total_bytes > 0:
                percent = downloaded_bytes / total_bytes * 100
            else:
                percent = 0

            if speed > 0 and total_bytes > 0:
                remaining_time = (total_bytes - downloaded_bytes) / speed
            else:
                remaining_time = 0

            import time
            now = time.time()
            if now - last_edit_time < 2:
                return

            last_edit_time = now

            progress_text = (
                f"**Downloading:** {percent:2.1f}%\n"
                f"**Downloaded:** {downloaded_bytes/1024/1024:2.2f}MB / {total_bytes/1024/1024:2.2f}MB\n"
                f"**Speed:** {speed/1024:2.2f} KiB/s\n"
                f"**ETA:** {int(remaining_time)}s"
            )

            future = asyncio.run_coroutine_threadsafe(
                _do_edit_message_text(progress_text),
                loop
            )

            try:
                future.result()
            except Exception as e:
                logging.warning(f"Failed to edit progress message: {e}")

    return hook


async def download_video(url: str, quality: str, app, chat_id: int, message_id: int):
    loop = asyncio.get_event_loop()

    def _download_video_sync(_url: str, _quality: str):
        progress_hook = create_progress_hook(app, chat_id, message_id, loop)

        info_opts = {
            'quiet': True,
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(info_opts) as ydl:
            info = ydl.extract_info(_url, download=False)

        native_mp4_available = False
        assert info
        for fmt in info.get('formats', []):
            ext = fmt.get('ext')
            if ext == 'mp4':
                native_mp4_available = True
                break

        with tempfile.TemporaryDirectory() as tmpdirname:
            logging.debug(f"Temp dir {tmpdirname} available")
            outtmpl = str(Path(tmpdirname) / '%(id)s.%(ext)s')

            if native_mp4_available:
                logging.debug("Use mp4 for video")
                ydl_opts = {
                    'outtmpl': outtmpl,
                    'format': f"bestvideo[ext=mp4][height={_quality}]+bestaudio[ext=m4a]/mp4",
                    'quiet': True,
                    'noplaylist': True,
                    'progress_hooks': [progress_hook],
                }
            else:
                ydl_opts = {
                    'outtmpl': outtmpl,
                    'format': f"bestvideo[height={_quality}]+bestaudio/best",
                    'quiet': True,
                    'noplaylist': True,
                    'progress_hooks': [progress_hook],
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4',
                    }],
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(_url, download=True)
                filename = ydl.prepare_filename(info)
                if not native_mp4_available:
                    filename = str(Path(filename).with_suffix('.mp4'))

            with open(filename, 'rb') as f:
                video_bytes = BytesIO(f.read())

            video_bytes.name = Path(filename).name
            video_bytes.seek(0)

        return video_bytes

    return await loop.run_in_executor(None, _download_video_sync, url, quality)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

