from bot.db.models import Cache
from typing import Tuple


async def get_cache(url: str, quality: int) -> Tuple[int, int]:
    cache_entry = await Cache.filter(url=url, quality=quality).first()
    if cache_entry:
        return cache_entry.chat_id, cache_entry.message_id
    return 0, 0


async def set_cache(url: str, quality: int, chat_id: int, message_id: int):
    cache_entry = await Cache.filter(url=url, quality=quality).first()
    if cache_entry:
        cache_entry.chat_id = chat_id
        cache_entry.message_id = message_id
        await cache_entry.save()
    else:
        await Cache.create(url=url, quality=quality, chat_id=chat_id, message_id=message_id)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
