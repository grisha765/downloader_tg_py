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


class Options(tortoise.models.Model):
    id = fields.IntField(pk=True)
    chat_id = fields.BigIntField()
    option_name = fields.CharField(max_length=50)
    value = fields.TextField()

    class Meta(tortoise.models.Model.Meta):
        table = "options"
        unique_together = ("chat_id", "option_name")

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
