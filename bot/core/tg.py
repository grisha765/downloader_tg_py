from bot.core.init import init_client
from bot.funcs.watchdog import watchdog_startup
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)

app = init_client()

async def start_bot():
    logging.info("Launching the bot...")
    await app.start()
    await watchdog_startup(app)
    logging.info("Bot have been started!")


async def stop_bot():
    logging.info("Stopping the bot...")
    await app.stop()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

