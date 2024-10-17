from db.models import SentVideo

async def get_last_sent_video(user_id, channel_url):
    sent_video = await SentVideo.filter(user_id=user_id, channel_url=channel_url).first()
    if sent_video:
        return sent_video.video_id
    return None

async def update_last_sent_video(user_id, channel_url, video_id):
    sent_video = await SentVideo.filter(user_id=user_id, channel_url=channel_url).first()
    if sent_video:
        sent_video.video_id = video_id
        await sent_video.save()
    else:
        await SentVideo.create(user_id=user_id, channel_url=channel_url, video_id=video_id)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
