import asyncio
from bot.core.helpers import safe_call, Common
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)

async def animate_message(message, base_text, started_event, refresh_rate=1.0):
    spinner_frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    i = 0
    try:
        while not started_event.is_set():
            frame = spinner_frames[i % len(spinner_frames)]
            i += 1
            try:
                await safe_call(
                    message.edit_text,
                    text= f"{frame} {base_text}"
                )
            except Exception as e:
                logging.warning(f"Spinner edit failed: {e}")
                return
            await asyncio.sleep(refresh_rate)
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
