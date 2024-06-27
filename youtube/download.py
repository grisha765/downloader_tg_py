import asyncio
import yt_dlp
import os

async def get_video_info(url):
    ydl_opts = {
        'format': 'best',
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = await asyncio.to_thread(ydl.extract_info, url, download=False)
        name = info_dict.get('title', 'N/A')
        duration = info_dict.get('duration', 'N/A')
        upload_date = info_dict.get('upload_date', 'N/A')
        description = info_dict.get('description', 'N/A')
        author = info_dict.get('uploader', 'N/A')
        thumbnail = info_dict.get('thumbnail', None)
        
        formats = info_dict.get('formats', [])
        qualities = {}
        
        for f in formats:
            if f.get('vcodec') != 'none':  # Check if the format contains video
                quality = f.get('format_note', None)
                filesize = f.get('filesize', None)
                
                if quality and filesize:
                    if quality not in qualities or qualities[quality][1] < filesize:
                        size_mb = filesize / (1024 * 1024)  # Convert to MB
                        size_str = f"{size_mb:.2f}Mb" if size_mb < 1024 else f"{size_mb / 1024:.2f}Gb"
                        qualities[quality] = (size_str, filesize)
        
        qualities_list = [f"{quality} - {data[0]}" for quality, data in qualities.items()]
        
        # Format the duration
        if duration != 'N/A':
            if duration < 60:
                duration_str = f"{duration} seconds"
            elif duration < 3600:
                minutes, seconds = divmod(duration, 60)
                duration_str = f"{minutes} minutes {seconds} seconds"
            else:
                hours, remainder = divmod(duration, 3600)
                minutes, seconds = divmod(remainder, 60)
                duration_str = f"{hours} hours {minutes} minutes {seconds}"
        else:
            duration_str = 'Unknown duration'
        
        video_info = {
            "name": name,
            "duration": duration_str,
            "date": upload_date if upload_date != 'N/A' else 'Unknown date',
            "description": description,
            "author": author if author != 'N/A' else 'Unknown author',
            "qualities": qualities_list,
            "thumbnail": thumbnail,
        }
        
        return video_info

async def download_video(url, quality):
    ydl_opts = {
        'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
        'outtmpl': '%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = await asyncio.to_thread(ydl.extract_info, url)
        await asyncio.to_thread(ydl.download, [url])
        file_path = os.path.join(os.getcwd(), f"{info['title']}.mp4")
    return file_path

async def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = await asyncio.to_thread(ydl.extract_info, url)
        await asyncio.to_thread(ydl.download, [url])
        file_path = os.path.join(os.getcwd(), f"{info['title']}.mp3")
    return file_path

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

