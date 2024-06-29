import asyncio
import yt_dlp
import os

from config import logging_config
logging = logging_config.setup_logging(__name__)

class MyLogger:
    def debug(self, msg):
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

async def download_video(url, quality):
    ydl_opts = {
        'format': f'bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=mp4]/best[height<={quality}]',
        'outtmpl': '/tmp/video_file.mp4',
        'extract_flat': 'discard_in_playlist',
        'fragment_retries': 10,
        'ignoreerrors': 'only_download',
        'postprocessors': [{'api': 'https://sponsor.ajay.app',
                         'categories': {'sponsor'},
                         'key': 'SponsorBlock',
                         'when': 'after_filter'},
                        {'force_keyframes': False,
                         'key': 'ModifyChapters',
                         'remove_sponsor_segments': {'sponsor'},},],
        'retries': 10,
        'logger': MyLogger(),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = await asyncio.to_thread(ydl.extract_info, url)
        await asyncio.to_thread(ydl.download, [url])
        file_path = os.path.join("/tmp", "video_file.mp4")
    return file_path

async def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '/tmp/audio_file.mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': MyLogger(),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = await asyncio.to_thread(ydl.extract_info, url)
        await asyncio.to_thread(ydl.download, [url])
        file_path = os.path.join("/tmp", "audio_file.mp3")
    return file_path

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

