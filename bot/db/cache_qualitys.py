from typing import Dict
from .models import CacheQuality


async def set_quality_size(url: str, quality: int, size: float):
    obj, created = await CacheQuality.get_or_create(
        url=url,
        resolution=quality,
        defaults={"size": size}
    )
    if not created:
        obj.size = size
        await obj.save()


async def set_qualitys(url: str, qualitys: Dict[int, float]):
    for resolution, size in qualitys.items():
        await set_quality_size(url, resolution, size)


async def get_qualitys(url: str) -> Dict[int, float]:
    records = (
        await CacheQuality
        .filter(url=url)
        .order_by("resolution")
        .values("resolution", "size")
    )
    
    result = {}
    for record in records:
        result[record["resolution"]] = record["size"]
    return result

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

