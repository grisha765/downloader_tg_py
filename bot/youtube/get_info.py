import asyncio
from bot.core.classes import Common

async def get_video_info(url: str) -> dict:
    loop = asyncio.get_event_loop()

    def _get_video_info_sync(_url: str) -> dict:
        ydl_opts = {
            'quiet': True,
            'noplaylist': True,
        }
        with Common.youtube(ydl_opts) as ydl:
            info = ydl.extract_info(_url, download=False)

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

        quality_size_mb = {
            height: round(size / (1024 * 1024), 2)
            for height, size in quality_size_dict.items()
        }

        sorted_quality_size_mb = dict(sorted(quality_size_mb.items()))
        return sorted_quality_size_mb

    return await loop.run_in_executor(None, _get_video_info_sync, url)

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
