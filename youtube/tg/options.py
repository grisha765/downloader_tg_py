from db.option import toggle_user_option, get_user_option
from config import logging_config
logging = logging_config.setup_logging(__name__)

async def sponsor_block_toggle(message):
    user_id = message.from_user.id
    option_name = 'sponsor'
    info_message = await toggle_user_option(user_id, option_name)
    logging.debug(f"{user_id}: {info_message}.")
    await message.reply_text(f"Option '{option_name}' toggled to {await get_user_option(user_id, option_name)}.")
