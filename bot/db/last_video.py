from bot.db.models import SendVideo


async def get_last_sent_video(user_id: int, channel_url: str) -> str:
    sent_video = await SendVideo.filter(user_id=user_id, channel_url=channel_url).first()
    if sent_video:
        return sent_video.video_url
    return ''


async def update_last_sent_video(user_id: int, channel_url: str, video_url: str):
    sent_video = await SendVideo.filter(user_id=user_id, channel_url=channel_url).first()
    if sent_video:
        sent_video.video_url = video_url
        await sent_video.save()
    else:
        await SendVideo.create(user_id=user_id, channel_url=channel_url, video_url=video_url)


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
