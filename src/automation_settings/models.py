from tortoise import Model, fields


class AutomationSettings(Model):
    id = fields.IntField(pk=True)

    key = fields.CharField(max_length=64, unique=True, index=True)
    value = fields.CharField(max_length=256)

    class Meta:
        table = "automation_settings"
