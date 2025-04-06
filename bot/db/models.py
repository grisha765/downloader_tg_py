import tortoise.models
from tortoise import fields


class Cache(tortoise.models.Model):
    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=255)
    quality = fields.CharField(max_length=50)
    chat_id = fields.BigIntField()
    message_id = fields.BigIntField()

    class Meta(tortoise.models.Model.Meta):
        table = "cache"
        unique_together = ("url", "quality")

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
