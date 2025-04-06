from bot.core.common import init_client
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)

app = init_client()

async def start_bot():
    logging.info("Launching the bot...")
    await app.start()


async def stop_bot():
    logging.info("Stopping the bot...")
    await app.stop()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

