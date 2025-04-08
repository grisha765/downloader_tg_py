from tortoise.exceptions import DoesNotExist
from bot.db.models import Options

async def set_option(chat_id: int, option_name: str, value: str) -> bool:
    try:
        await Options.update_or_create(
            defaults={"value": value},
            chat_id=chat_id,
            option_name=option_name
        )
        return True
    except Exception:
        return False


async def get_option(chat_id: int, option_name: str) -> str:
    try:
        chat_option = await Options.get(chat_id=chat_id, option_name=option_name)
        return chat_option.value
    except DoesNotExist:
        return ''
    except Exception:
        return ''


async def del_option(chat_id: int, option_name: str) -> bool:
    try:
        chat_option = await Options.get(chat_id=chat_id, option_name=option_name)
        await chat_option.delete()
        return True
    except DoesNotExist:
        return False
    except Exception:
        return False

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
