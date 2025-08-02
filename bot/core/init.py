from bot.core.handlers import init_handlers
from bot.funcs.watchdog import watchdog_startup
from pyrogram.client import Client
from bot.config.config import Config
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)


app = Client(
    name="bot",
    api_id=Config.tg_id,
    api_hash=Config.tg_hash,
    bot_token=Config.tg_token
)
init_handlers(app)


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

