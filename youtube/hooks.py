import re, asyncio
from config import logging_config
logging = logging_config.setup_logging(__name__)

async def update_progress(message, progress_hook, form):
    last_message = None
    while progress_hook.progress < 100:
        try:
            new_message = f"🟥Download {form}: {progress_hook.progress}%\n🟥Send video to telegram..."
            if new_message != last_message:
                logging.debug(f"Updating message: {progress_hook.progress}%")
                await message.edit(new_message)
                last_message = new_message
            await asyncio.sleep(2)
        except Exception as e:
            logging.error(f"Error updating progress: {e}")
            break

class ProgressHook:
    def __init__(self):
        self.progress = 0
        self.downloaded_bytes = 0
        self.update_allowed = True

    def hook(self, d):
        if d['status'] == 'downloading' and self.update_allowed:
            # Remove ANSI color codes
            percent_str = re.sub(r'\x1b\[[0-9;]*m', '', d['_percent_str'])
            self.progress = float(percent_str.strip('%'))
            self.downloaded_bytes = d['downloaded_bytes']
        elif d['status'] == 'finished':
            logging.debug(f"Download finished")
            self.progress = 100
            self.update_allowed = False

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
