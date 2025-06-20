import yt_dlp, httpx, asyncio
from collections import defaultdict

class Common:
    select_video = {}
    user_semaphores = defaultdict(lambda: asyncio.BoundedSemaphore(5))
    user_tasks = {}
    youtube = yt_dlp.YoutubeDL
    http = httpx.AsyncClient()
