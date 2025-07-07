import yt_dlp, httpx, asyncio
from collections import defaultdict
from typing import cast
from pyrogram.errors import FloodWait

class Common:
    select_video = {}
    user_semaphores = defaultdict(lambda: asyncio.BoundedSemaphore(5))
    user_tasks = {}
    youtube = yt_dlp.YoutubeDL
    http = httpx.AsyncClient()


async def safe_call(func, *args, **kwargs):
    for _ in range(5):
        try:
            return await func(*args, **kwargs)
        except FloodWait as e:
            wait_sec: int = cast(int, e.value)
            await asyncio.sleep(wait_sec + 1)
    raise


