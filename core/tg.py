import asyncio
from config.config import Config
from pyrogram import Client, filters
from youtube.tg_func import func_message, func_video_selection, func_audio_selection, sponsor_block_toggle, add_channel_command, del_channel_command, process_user_channels
from config import logging_config
logging = logging_config.setup_logging(__name__)

app = Client("bot", api_id=Config.tg_id, api_hash=Config.tg_hash, bot_token=Config.tg_token)

@app.on_message(filters.command("sponsor") & filters.private)
async def handle_sponsor_block_toggle(client, message):
    await sponsor_block_toggle(message)

@app.on_message(filters.command("addchannel") & filters.private)
async def handle_add_channel_command(client, message):
    await add_channel_command(message)

@app.on_message(filters.command("addchannel") & filters.private)
async def handle_del_channel_command(client, message):
    await del_channel_command(message)

@app.on_message(filters.text & filters.private)
async def handle_message(client, message):
    await func_message(message)

@app.on_callback_query(filters.regex(r'^quality_\d+$'))
async def handle_video_selection(client, callback_query):
    await func_video_selection(callback_query, app)

@app.on_callback_query(filters.regex(r'^audio$'))
async def handle_audio_selection(client, callback_query):
    await func_audio_selection(callback_query, app)

async def periodic_task(app):
    while True:
        await process_user_channels(app)
        await asyncio.sleep(Config.notify_timeout)

async def start_periodic_task(app):
    await app.start()
    await periodic_task(app)

def run_bot():
    logging.info("Launching the bot...")
    app.run(start_periodic_task(app))

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

