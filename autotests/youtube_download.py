from youtube.tg.base import func_message
from youtube.tg.video import download_video_tg
from youtube.get_id import get_url_id
from typing import List, Union
from pyrogram import Client
from pyrogram.types import Message
from config import logging_config
logging = logging_config.setup_logging(__name__)

chat_id = 998163723
quality = "720"

async def parse_id_200(app: Client, id_200: List[int], from_chat: Union[str, int]):
    msgs = await app.get_messages(chat_id=from_chat, message_ids=id_200)
    for msg in msgs:
        yield msg

async def get_msgs_bot(app: Client, from_chat: Union[str, int], start: int, stop: int):
    id_200: List[int] = []
    if start < stop:
        step = 1
        total = stop - start
    elif start > stop:
        step = -1
        total = start - stop
    else:
        msg = await app.get_messages(chat_id=from_chat, message_ids=[start])
        assert isinstance(msg, Message)
        yield msg
        return
    
    completed = 0
    for num in range(start, stop + step, step):
        if len(id_200) < 200:
            id_200.append(num)
        else:
            async for msg in parse_id_200(app, id_200, from_chat):
                yield msg
            completed += 200
            id_200 = [num]
    
    async for msg in parse_id_200(app, id_200, from_chat):
        yield msg

async def run_test():
    async with Client("bot") as app:
        async for message in get_msgs_bot(app, chat_id, 1000, 1027):
            if message.text and "https://" in message.text:
                message_id = message.id
                url_id = get_url_id(message.text)
                logging.debug(f"Message ID with link: {message_id}")
                logging.debug(f"Message text: {message.text}")
                query_message = await func_message(message)
                download_path = "./"
                video_message = await download_video_tg(app, url_id, quality, query_message, 123456, 39, download_path)
                assert video_message == f"{download_path}/video-{url_id}-{quality}.mp4", f"Expected: cpation video_message not exactly to the specified parameters."
                logging.info("Test passed!")
                return

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
