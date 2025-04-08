from typing import Dict
from .models import CacheQuality


async def set_qualitys(url: str, qualitys: Dict[int, float]):
    await CacheQuality.filter(url=url).delete()

    for resolution, size in qualitys.items():
        await CacheQuality.create(
            url=url,
            resolution=resolution,
            size=size
        )


async def get_qualitys(url: str) -> Dict[int, float]:
    records = await CacheQuality.filter(url=url).values("resolution", "size")
    return {record["resolution"]: record["size"] for record in records}


async def set_quality_size(url: str, quality: int, size: float):
    obj, created = await CacheQuality.get_or_create(
        url=url,
        resolution=quality,
        defaults={"size": size}
    )
    if not created:
        obj.size = size
        await obj.save()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

