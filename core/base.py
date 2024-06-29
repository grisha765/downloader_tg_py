from youtube.download import download_audio, download_video, get_video_info

async def run_youtube():
    url = input("Введите URL видео: ")
    info = await get_video_info(url)

    qualities = info["qualities"]
    print("Доступные качества видео:")
    for quality in qualities:
        print(quality)
    
    choice = input("Выберите качество или введите 'audio' для загрузки только аудио: ")
    
    if choice == 'audio':
        await download_audio(url)
    else:
        try:
            available_qualities = [quality.replace('p', '').split(' - ')[0] for quality in qualities]
            
            choice = str(choice)
            await download_video(url, choice)
        except ValueError:
            print("Неверный выбор качества!")

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

