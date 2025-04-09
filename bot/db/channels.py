from bot.db.models import Channels
from tortoise.exceptions import IntegrityError


async def add_channel(user_id: int, url: str) -> bool:
    try:
        channel, created = await Channels.get_or_create(user_id=user_id, url=url)
        if created:
            return True
        else:
            return False
    except IntegrityError:
        return False


async def del_channel(user_id: int, url: str) -> bool:
    channel = await Channels.filter(user_id=user_id, url=url).first()
    if channel:
        await channel.delete()
        return True
    else:
        return False


async def get_channels(user_id: int):
    channels = await Channels.filter(user_id=user_id).all()
    return [channel.url for channel in channels]


async def get_all_channels():
    channels = await Channels.all()
    user_channels = {}
    for channel in channels:
        if channel.user_id not in user_channels:
            user_channels[channel.user_id] = []
        user_channels[channel.user_id].append(channel.url)
    return user_channels.items()


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
