from db.channel import add_channel, del_channel, get_channels
from config import logging_config
logging = logging_config.setup_logging(__name__)

async def add_channel_command(message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        await message.reply_text("Please provide the channel URL.")
        return

    url = message.command[1]
    info_message = await add_channel(user_id, url)
    logging.debug(f"{user_id}: {info_message}")
    await message.reply_text(f"A channel with URL {url} has been added to the database.\n{await get_channels(user_id)}")

async def del_channel_command(message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        await message.reply_text("Please provide the channel URL.")
        return

    url = message.command[1]
    info_message = await del_channel(user_id, url)
    logging.debug(f"{user_id}: {info_message}")
    await message.reply_text(f"A channel with URL {url} has been deleted from database.\n{await get_channels(user_id)}")
