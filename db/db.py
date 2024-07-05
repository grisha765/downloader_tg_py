from config.config import Config
from tortoise import Tortoise

async def init():
    await Tortoise.init(
        db_url=f'sqlite://{Config.tg_token[:10]}.db',
        modules={'models': ['db.models']}
    )
    await Tortoise.generate_schemas()

async def close():
    await Tortoise.close_connections()

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
