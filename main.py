import asyncio
from config.config import Config
from config import logging_config
logging = logging_config.setup_logging(__name__)

logging.info(f"Script initialization, logging level: {Config.log_level}")

if __name__ == '__main__':
    if Config.tg_token != 'None':
        from core.tg import run_bot
        run_bot()
    else:
        from core.base import run_youtube
        asyncio.run(run_youtube())
