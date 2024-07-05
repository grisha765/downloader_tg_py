from db.models import Channel

async def add_channel(user_id: int, url: str):
    try:
        channel, created = await Channel.get_or_create(user_id=user_id, url=url)
        if created:
            return f"Channel {url} added for user {user_id}."
        else:
            return f"Channel {url} already exists for user {user_id}."
    except IntegrityError:
        return f"Channel {url} already exists for user {user_id}."

async def del_channel(user_id: int, url: str):
    channel = await Channel.filter(user_id=user_id, url=url).first()
    if channel:
        await channel.delete()
        return f"Channel {url} deleted for user {user_id}."
    else:
        return f"Channel {url} does not exist for user {user_id}."

async def get_channels(user_id: int):
    channels = await Channel.filter(user_id=user_id).all()
    return [channel.url for channel in channels]

async def get_all_channels():
    channels = await Channel.all()
    user_channels = {}
    for channel in channels:
        if channel.user_id not in user_channels:
            user_channels[channel.user_id] = []
        user_channels[channel.user_id].append(channel.url)
    return user_channels.items()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
