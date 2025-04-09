import tortoise.models
from tortoise import fields


class Cache(tortoise.models.Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255)
    quality = fields.BigIntField()
    chat_id = fields.BigIntField()
    message_id = fields.BigIntField()

    class Meta(tortoise.models.Model.Meta):
        table = "cache"
        unique_together = ("url", "quality")


class CacheQuality(tortoise.models.Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255)
    resolution = fields.IntField()
    size = fields.FloatField()

    class Meta(tortoise.models.Model.Meta):
        table = "cache_qualitys"
        unique_together = ("url", "resolution")


class Options(tortoise.models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField()
    option_name = fields.CharField(max_length=50)
    value = fields.TextField()

    class Meta(tortoise.models.Model.Meta):
        table = "options"
        unique_together = ("user_id", "option_name")


class Channels(tortoise.models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField()
    url = fields.CharField(max_length=255)

    class Meta(tortoise.models.Model.Meta):
        table = "channels"
        unique_together = ("user_id", "url")


class SendVideo(tortoise.models.Model):
    id = fields.IntField(pk=True)
    user_id = fields.BigIntField()
    channel_url = fields.CharField(max_length=255)
    video_url = fields.CharField(max_length=255)

    class Meta(tortoise.models.Model.Meta):
        table = "send_videos"
        unique_together = ("user_id", "channel_url")


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
