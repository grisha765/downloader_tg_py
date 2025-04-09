import asyncio
from bot.db.options import get_option
from bot.db.channels import get_channels
from bot.db.last_video import get_last_sent_video, update_last_sent_video
from bot.youtube.channel_scrap import channel_scrap
from bot.youtube.get_info import get_video_info
from bot.funcs.video_msg import download_video_msg
from bot.config import logging_config
logging = logging_config.setup_logging(__name__)


async def auto_video_msg(client, user_id):
    refresh_map = {
        "15min": 15 * 60,
        "30min": 30 * 60,
        "1h":    60 * 60,
        "6h":    6 * 60 * 60,
        "12h":   12 * 60 * 60,
        "1d":    24 * 60 * 60,
    }
    current_value = await get_option(user_id, "refresh") or "15min"
    refresh_in_seconds = refresh_map.get(current_value, refresh_map["15min"])

    try:
        while True:
            for channel_url in await get_channels(user_id):
                last_sent_video = await get_last_sent_video(user_id, channel_url)
                new_video = await channel_scrap(channel_url)

                if new_video:
                    if last_sent_video != new_video:
                        logging.debug(f'{user_id}: new video found: {new_video}')
                        qualitys = await get_video_info(new_video)
                        resolutions = list(qualitys.keys())
                        quality = await get_option(user_id, "quality") or "Medium"

                        selected = None
                        match quality:
                            case 'Low':
                                selected = resolutions[0]
                            case 'Medium':
                                if 720 in resolutions:
                                    selected = 720
                                else:
                                    mid_index = len(resolutions) // 2
                                    selected = resolutions[mid_index]
                            case 'High':
                                filtered = [(res, val) for res, val in qualitys.items() if val < 2000.00]
                                if filtered:
                                    selected = max(filtered, key=lambda x: x[0])[0]
                                else:
                                    selected = 1080
                        logging.debug(f'{user_id}: Quality selected: {selected}')

                        msg = await client.send_message(
                            chat_id=user_id,
                            text=f"Latest video: {new_video}\n{qualitys}\n{selected}"
                        )


                        await download_video_msg(client, msg, msg.id, new_video, selected)
                        await update_last_sent_video(user_id, channel_url, new_video)

            await asyncio.sleep(refresh_in_seconds)
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

