from db.models import UserOption
from tortoise.exceptions import IntegrityError

async def toggle_user_option(user_id: int, option_name: str):
    try:
        user_option, created = await UserOption.get_or_create(user_id=user_id, option_name=option_name, defaults={"value": True})
        if created:
            user_option.value = True
            await user_option.save()
            return f"Option {option_name} for user {user_id} set to True."
        else:
            user_option.value = not user_option.value
            await user_option.save()
            return f"Option {option_name} for user {user_id} toggled to {user_option.value}."
    except IntegrityError as e:
        return f"Failed to toggle option {option_name} for user {user_id}: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

async def get_user_option(user_id: int, option_name: str):
    user_option = await UserOption.filter(user_id=user_id, option_name=option_name).first()
    if user_option:
        return user_option.value
    else:
        return False

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
