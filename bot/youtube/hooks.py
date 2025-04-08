import asyncio, time
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)

def create_progress_hook(app, chat_id, message_id, loop, download_started_event):
    last_edit_time = 0

    async def _async_set_event(event):
        event.set()

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
            if not download_started_event.is_set():
                future = asyncio.run_coroutine_threadsafe(
                    _async_set_event(download_started_event),
                    loop
                )
                future.result()

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

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
