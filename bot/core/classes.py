import yt_dlp, httpx

class Common:
    select_video = {}
    youtube = yt_dlp.YoutubeDL
    http = httpx.AsyncClient()
