import asyncio
from pyrogram import Client
from config.config import Config
from config import logging_config
logging = logging_config.setup_logging(__name__)

api_id = Config.test_tg_id
api_hash = Config.test_tg_hash
test_chat_id = int(Config.tg_token[:10])
youtube_link = "https://www.youtube.com/watch?v=w8dg2f_wiuk"

async def run_test():
    async with Client("test_user", api_id=api_id, api_hash=api_hash) as app:
        async for dialog in app.get_dialogs():
            if dialog.chat.id == test_chat_id:
                break
        else:
            raise ValueError("The userbot has not interacted with the specified bot before")

        sent_message = await app.send_message(test_chat_id, youtube_link)
        logging.debug("Sent message with YouTube link: %s", sent_message)
        await asyncio.sleep(5)

        buttons_callback_data = []
        message_id = None

        async for message in app.get_chat_history(test_chat_id, limit=1):
            message_id = message.id
            if message.reply_markup and message.reply_markup.inline_keyboard:
                buttons = message.reply_markup.inline_keyboard
                logging.debug("Found inline keyboard: %s", buttons)
                for row in buttons:
                    for button in row:
                        callback_data = button.callback_data
                        buttons_callback_data.append(callback_data)
                        break
                    break
                break
        if buttons_callback_data:
            logging.debug("Collected callback data: %s", buttons_callback_data)
            try:
                response = await asyncio.wait_for(
                    app.request_callback_answer(
                        chat_id=test_chat_id,
                        message_id=message_id,
                        callback_data=buttons_callback_data[0]
                    ),
                    timeout=10.0
                )
                logging.debug("Simulated button click with callback data: %s, response: %s", buttons_callback_data[0], response)
            except asyncio.TimeoutError:
                logging.error("Запрос callback превысил время ожидания.")
            except Exception as e:
                logging.error("Error simulating button click: %s", e)
        else:
            logging.error("No inline buttons found with callback data.")
        logging.info("Test passed!")
        await app.stop()
        return


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
