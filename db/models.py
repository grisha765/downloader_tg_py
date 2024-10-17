from tortoise import fields
from tortoise.models import Model

class Cache(Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255)
    quality = fields.CharField(max_length=50)
    chat_id = fields.BigIntField()
    message_id = fields.BigIntField()

    class Meta:
        table = "cache"
        unique_together = ("url", "quality")

class Channel(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField()
    url = fields.CharField(max_length=255)

    class Meta:
        table = "channel"
        unique_together = ("user_id", "url")

class SentVideo(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField()
    channel_url = fields.CharField(max_length=255)
    video_id = fields.CharField(max_length=255)

    class Meta:
        table = "sent_videos"
        unique_together = ("user_id", "channel_url")

class UserOption(Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField()
    option_name = fields.CharField(max_length=50)
    value = fields.BooleanField()

    class Meta:
        table = "user_option"
        unique_together = ("user_id", "option_name")

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
