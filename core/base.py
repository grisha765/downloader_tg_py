from config import logging_config
logging = logging_config.setup_logging(__name__)
from youtube.download import download_audio, download_video, get_video_info

async def run_youtube():
    logging.info("Start base.py...")
    url = input("Введите URL видео: ")
    info = await get_video_info(url)

    qualities = info["qualities"]
    print("Доступные качества видео:")
    for quality in qualities:
        print(quality)
    
    choice = input("Выберите качество или введите 'audio' для загрузки только аудио: ")
    
    if choice == 'audio':
        logging.info("Download audio...")
        file_mame = await download_audio(url)
        logging.info(f"Audio as {file_mame} uploaded successfully!")
    else:
        try:
            choice = str(choice)
            logging.info("Download video...")
            file_mame = await download_video(url, choice)
            logging.info(f"Video as {file_mame} uploaded successfully!")
        except ValueError:
            logging.error(f"Wrong choice of quality!")

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

