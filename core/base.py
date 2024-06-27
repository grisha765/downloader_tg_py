from youtube.download import download_audio, download_video, get_video_info
async def run_youtube():
    url = input("Введите URL видео: ")
    info = await get_video_info(url)

    print("Доступные качества видео:", info)
    choice = input("Выберите качество или введите 'audio' для загрузки только аудио: ")
    
    if choice == 'audio':
        await download_audio(url)
    else:
        try:
            choice = int(choice)
            if choice in available_qualities:
                await download_video(url, choice)
            else:
                print("Выбранное качество недоступно!")
        except ValueError:
            print("Неверный выбор качества!")

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
