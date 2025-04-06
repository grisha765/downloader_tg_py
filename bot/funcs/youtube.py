import yt_dlp, tempfile
from pathlib import Path
from io import BytesIO
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)


def download_video(url: str) -> BytesIO:
    info_opts = {
        'quiet': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(info_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    
    native_mp4_available = False
    for fmt in info['formats']:
        ext = fmt.get('ext')
        logging.debug(f"Video format: {ext}")
        if ext == 'mp4':
            native_mp4_available = True
            break

    with tempfile.TemporaryDirectory() as tmpdirname:
        outtmpl = str(Path(tmpdirname) / '%(id)s.%(ext)s')
        
        if native_mp4_available:
            ydl_opts = {
                'outtmpl': outtmpl,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'quiet': True,
                'noplaylist': True,
            }
        else:
            ydl_opts = {
                'outtmpl': outtmpl,
                'format': 'bestvideo+bestaudio/best',
                'quiet': True,
                'noplaylist': True,
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4',
                }],
            }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not native_mp4_available:
                filename = str(Path(filename).with_suffix('.mp4'))
        
        with open(filename, 'rb') as f:
            video_bytes = BytesIO(f.read())
        
        video_bytes.name = Path(filename).name
        video_bytes.seek(0)
    
    return video_bytes

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

