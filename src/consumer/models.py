from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Consumer(Model):
    id = fields.CharField(max_length=64, pk=True)
    name = fields.CharField(max_length=256)

    components: fields.ReverseRelation["Component"]
    state: fields.OneToOneRelation["State"]


class Component(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32)

    consumer: fields.ForeignKeyRelation["Consumer"] = fields.ForeignKeyField(
        "models.Consumer", related_name="components", on_delete=fields.OnDelete.CASCADE
    )


class State(Model):
    id = fields.IntField(pk=True)

    consumer: fields.OneToOneRelation["Consumer"] = fields.OneToOneField(
        "models.Consumer", related_name="state", on_delete=fields.OnDelete.CASCADE
    )


Consumer_Pydantic = pydantic_model_creator(Consumer, name="Consumer")
ConsumerIn_Pydantic = pydantic_model_creator(Consumer, name="ConsumerIn")
ConsumerOut_Pydantic = pydantic_model_creator(Consumer, name="ConsumerOut")

# Component_Pydantic = pydantic_model_creator(Component, name="Component")
# ComponentIn_Pydantic = pydantic_model_creator(Component, name="ComponentIn")
# ComponentOut_Pydantic = pydantic_model_creator(Component, name="ComponentOut")
