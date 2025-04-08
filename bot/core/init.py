import pyrogram.filters
import pyrogram.handlers.message_handler
from pyrogram.client import Client
from bot.config.config import Config
from bot.funcs.commands import start_command, get_video_command, download_video_command, options_command, options_buttons, options_set_buttons


def init_client() -> Client:
    app = Client(
        name="bot",
        api_id=Config.tg_id,
        api_hash=Config.tg_hash,
        bot_token=Config.tg_token
    )
    app.add_handler(
        pyrogram.handlers.message_handler.MessageHandler(
            start_command,
            pyrogram.filters.command("start") &
                pyrogram.filters.private
        )
    )
    app.add_handler(
        pyrogram.handlers.message_handler.MessageHandler(
            options_command,
            pyrogram.filters.command("settings") &
                pyrogram.filters.private
        )
    )
    app.add_handler(
        pyrogram.handlers.message_handler.MessageHandler(
            get_video_command,
            pyrogram.filters.text &
                pyrogram.filters.private
        )
    )
    app.add_handler(
        pyrogram.handlers.callback_query_handler.CallbackQueryHandler(
            download_video_command,
            pyrogram.filters.regex(r"^quality_")
        )
    )
    app.add_handler(
        pyrogram.handlers.callback_query_handler.CallbackQueryHandler(
            options_buttons,
            pyrogram.filters.regex(r"^option_")
        )
    )
    app.add_handler(
        pyrogram.handlers.callback_query_handler.CallbackQueryHandler(
            options_set_buttons,
            pyrogram.filters.regex(r"^set_option_")
        )
    )
    return app

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

