import yt_dlp, httpx

class Common:
    select_video = {}
    user_tasks = {}
    youtube = yt_dlp.YoutubeDL
    http = httpx.AsyncClient()
