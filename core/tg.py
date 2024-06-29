from config.config import Config
from pyrogram import Client, filters
from youtube.tg_func import func_message, func_video_selection, func_audio_selection
from config import logging_config
logging = logging_config.setup_logging(__name__)

app = Client("bot", api_id=Config.tg_id, api_hash=Config.tg_hash, bot_token=Config.tg_token)

@app.on_message(filters.text & filters.private)
async def handle_message(client, message):
    await func_message(message)

@app.on_callback_query(filters.regex(r'^quality_\d+$'))
async def handle_video_selection(client, callback_query):
    await func_video_selection(callback_query, app)

@app.on_callback_query(filters.regex(r'^audio$'))
async def handle_audio_selection(client, callback_query):
    await func_audio_selection(callback_query, app)

def run_bot():
    logging.info("Запуск бота...")
    app.run()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

