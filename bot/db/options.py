from tortoise.exceptions import DoesNotExist
from bot.db.models import Options

async def set_option(user_id: int, option_name: str, value: str) -> bool:
    try:
        await Options.update_or_create(
            defaults={"value": value},
            user_id=user_id,
            option_name=option_name
        )
        return True
    except Exception:
        return False


async def get_option(user_id: int, option_name: str) -> str:
    try:
        chat_option = await Options.get(user_id=user_id, option_name=option_name)
        return chat_option.value
    except DoesNotExist:
        return ''
    except Exception:
        return ''


async def del_option(user_id: int, option_name: str) -> bool:
    try:
        chat_option = await Options.get(user_id=user_id, option_name=option_name)
        await chat_option.delete()
        return True
    except DoesNotExist:
        return False
    except Exception:
        return False


async def get_values(option_name: str) -> dict:
    options = await Options.filter(option_name=option_name).all()
    return {opt.user_id: opt.value for opt in options}


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
