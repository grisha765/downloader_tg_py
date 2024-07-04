import asyncio, yt_dlp, re

from youtube.hooks import ProgressHook
from config import logging_config
logging = logging_config.setup_logging(__name__)

class MyLogger:
    def __init__(self):
        self.last_percentage = None

    def debug(self, msg):
        match = re.search(r'(\d+\.\d+)%', msg)
        if match:
            percentage = match.group(1)
            if self.last_percentage != percentage:
                print(f"\rDownloading: {percentage}%", end='', flush=True)
                self.last_percentage = percentage
        else:
            logging.debug(msg)

    def info(self, msg):
        logging.info(msg)

    def warning(self, msg):
        logging.warning(msg)

    def error(self, msg):
        logging.error(msg)

async def get_video_info(url):
    ydl_opts = {
        'format': 'best',
        'logger': MyLogger(),
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
        name = info_dict.get('title', 'N/A')
        duration = info_dict.get('duration', 'N/A')
        upload_date = info_dict.get('upload_date', 'N/A')
        author = info_dict.get('uploader', 'N/A')
        thumbnail = info_dict.get('thumbnail', None)
        
        formats = info_dict.get('formats', [])
        qualities = {}
        
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('ext') == 'webm':
                resolution = f.get('height', 'Unknown')
                filesize = f.get('filesize', None)
                
                if resolution != 'Unknown':
                    if resolution not in qualities:
                        qualities[resolution] = {'filesize': 0, 'size_str': 'Unknown size'}
                    
                    if filesize and (qualities[resolution]['filesize'] < filesize):
                        size_mb = filesize / (1024 * 1024)
                        size_str = f"{size_mb:.2f}Mb" if size_mb < 1024 else f"{size_mb / 1024:.2f}Gb"
                        qualities[resolution] = {'filesize': filesize, 'size_str': size_str}
        
        qualities_list = [f"{resolution}p - {data['size_str']}" for resolution, data in qualities.items()]
        
        if duration != 'N/A':
            if duration < 60:
                duration_str = f"{duration} seconds"
            elif duration < 3600:
                minutes, seconds = divmod(duration, 60)
                duration_str = f"{minutes} minutes {seconds} seconds"
            else:
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)
                duration_str = f"{hours} hours {minutes} minutes {seconds} seconds"
        else:
            duration_str = 'Unknown duration'
        
        video_info = {
            "name": name,
            "duration": duration_str,
            "date": upload_date if upload_date != 'N/A' else 'Unknown date',
            "author": author if author != 'N/A' else 'Unknown author',
            "qualities": qualities_list,
            "thumbnail": thumbnail,
        }
        
        return video_info

def get_url_id(url):
    if "youtube.com" in url:
        return url.split('v=')[-1]
    elif "youtu.be" in url:
        return url.split('/')[-1]
    else:
        return "unknown_id"

async def download_video(url, quality, progress_hook, sponsor = True):
    url_id = get_url_id(url)
    if sponsor == True:
        sponsor_post = {
                    'postprocessors': [{'api': 'https://sponsor.ajay.app',
                         'categories': {'sponsor'},
                         'key': 'SponsorBlock',
                         'when': 'after_filter'},
                        {'force_keyframes': False,
                         'key': 'ModifyChapters',
                         'remove_sponsor_segments': {'sponsor'},},],
        }
    else:
        sponsor_post = {}

    ydl_opts = {
        'format': f'bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=mp4]/best[height<={quality}]',
        'outtmpl': f'video-{url_id}-{quality}.mp4',
        'extract_flat': 'discard_in_playlist',
        'fragment_retries': 10,
        'ignoreerrors': 'only_download',
        'retries': 10,
        'logger': MyLogger(),
        'progress_hooks': [progress_hook.hook],
        **sponsor_post
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = await asyncio.to_thread(ydl.extract_info, url)
        await asyncio.to_thread(ydl.download, [url])
        file_path = f'video-{url_id}-{quality}.mp4'
    return file_path

async def download_audio(url, progress_hook):
    url_id = get_url_id(url)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'audio-{url_id}',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': MyLogger(),
        'progress_hooks': [progress_hook.hook],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = await asyncio.to_thread(ydl.extract_info, url)
        await asyncio.to_thread(ydl.download, [url])
        file_path = f'audio-{url_id}.mp3'
    return file_path

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

