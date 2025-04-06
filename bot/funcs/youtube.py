import yt_dlp, tempfile
from pathlib import Path
from io import BytesIO
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)


def get_video_info(url: str) -> dict:
    ydl_opts = {
        'quiet': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    quality_size_dict = {}
    assert info
    for fmt in info.get('formats', []):
        height = fmt.get('height')
        if height is None:
            continue
        size = fmt.get('filesize') or fmt.get('filesize_approx')
        if size is None:
            continue
        if height in quality_size_dict:
            quality_size_dict[height] = max(quality_size_dict[height], size)
        else:
            quality_size_dict[height] = size

    quality_size_mb = {height: round(size / (1024 * 1024), 2)
                       for height, size in quality_size_dict.items()}

    sorted_quality_size_mb = dict(sorted(quality_size_mb.items()))
    return sorted_quality_size_mb


def download_video(url: str, quality: str) -> BytesIO:
    info_opts = {
        'quiet': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(info_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    
    native_mp4_available = False
    assert info
    for fmt in info.get('formats', []):
        ext = fmt.get('ext')
        logging.debug(f"Video format: {ext}")
        if ext == 'mp4':
            native_mp4_available = True
            break

    with tempfile.TemporaryDirectory() as tmpdirname:
        logging.debug(f"Temp dir {tmpdirname} avalible")
        outtmpl = str(Path(tmpdirname) / '%(id)s.%(ext)s')
        
        if native_mp4_available:
            logging.debug("Use mp4 for video")
            ydl_opts = {
                'outtmpl': outtmpl,
                'format': f"bestvideo[ext=mp4][height={quality}]+bestaudio[ext=m4a]/mp4",
                'quiet': True,
                'noplaylist': True,
            }
        else:
            ydl_opts = {
                'outtmpl': outtmpl,
                'format': f"bestvideo[height={quality}]+bestaudio/best",
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

