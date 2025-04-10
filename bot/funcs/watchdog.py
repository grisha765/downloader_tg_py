import asyncio
from bot.funcs.watchdog_msg import watchdog_video_msg
from bot.funcs.options import options_menu, option_set
from bot.db.options import get_values
from bot.core.classes import Common
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)


async def watchdog_switch(client, callback_query):
    user_id = callback_query.from_user.id
    if user_id in Common.user_tasks:
        Common.user_tasks[user_id].cancel()
        Common.user_tasks.pop(user_id, None)
        await callback_query.answer("Watchdog videos stop.")
        logging.debug(f'{user_id}: Watchdog videos task stop')
        await option_set(callback_query, 'watchdog', 'False')
    else:
        Common.user_tasks[user_id] = asyncio.create_task(watchdog_video_msg(client, user_id))
        await callback_query.answer("Watchdog videos start.")
        logging.debug(f'{user_id}: Watchdog videos task start')
        await option_set(callback_query, 'watchdog', 'True')


async def watchdog_startup(client):
    values = await get_values('watchdog')
    for user_id, value in values.items():
        if value == 'True':
            Common.user_tasks[user_id] = asyncio.create_task(watchdog_video_msg(client, user_id))
            logging.debug(f'{user_id}: Watchdog videos task autostart')


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

