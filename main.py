import asyncio
from db.db import init, close
from config.config import Config
from config import logging_config
logging = logging_config.setup_logging(__name__)

logging.info(f"Script initialization, logging level: {Config.log_level}")

async def main():
    from core.tg import start_bot
    await init()
    await start_bot()
    await close()

if __name__ == '__main__':
    if Config.tg_token != 'None':
        asyncio.run(main())
