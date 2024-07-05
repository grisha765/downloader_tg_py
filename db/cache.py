from db.models import Cache

async def get_cache(url, quality):
    cache_entry = await Cache.filter(url=url, quality=quality).first()
    if cache_entry:
        return cache_entry.chat_id, cache_entry.message_id
    return None, None

async def set_cache(url, quality, chat_id, message_id):
    cache_entry = await Cache.filter(url=url, quality=quality).first()
    if cache_entry:
        cache_entry.chat_id = chat_id
        cache_entry.message_id = message_id
        await cache_entry.save()
        return f"Cache updated for URL: {url}, Quality: {quality}, Chat ID: {chat_id}, Message ID: {message_id}."
    else:
        await Cache.create(url=url, quality=quality, chat_id=chat_id, message_id=message_id)
        return f"Cache created for URL: {url}, Quality: {quality}, Chat ID: {chat_id}, Message ID: {message_id}."

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
