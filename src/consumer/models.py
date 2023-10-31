from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator

from src.core.definitions import ConsumerMode, ConsumerStatus, ConsumerType


class Consumer(Model):
    id = fields.IntField(max_length=64, pk=True)

    name = fields.CharField(max_length=256, unique=True, index=True)
    priority = fields.IntField(default=0, unique=True)

    minimum_uninterrupted_runtime = fields.SmallIntField(default=0)
    maximum_runtime_per_day = fields.SmallIntField(default=0)

    components: fields.ReverseRelation["ConsumerComponent"]
    state: fields.OneToOneRelation["ConsumerState"]
    runtimes: fields.ReverseRelation["ConsumerRuntime"]

    def consumer_type(self) -> ConsumerType:
        return ConsumerType.SCC if len(self.components) == 1 else ConsumerType.MCC

    class Meta:
        computed = ["consumer_type"]


class ConsumerComponent(Model):
    id = fields.IntField(pk=True)

    name = fields.CharField(max_length=32)

    consumption = fields.SmallIntField(description="Consumption of the component [W]")
    running = fields.BooleanField(
        default=False,
        description="Describes whether this component is currently running ",
    )

    # TODO: This is Shelly specific move into separate table/model (e.g., switch -> sub model is shelly)
    ip = fields.CharField(max_length=64)
    relais = fields.SmallIntField()

    consumer: fields.ForeignKeyRelation["Consumer"] = fields.ForeignKeyField(
        "models.Consumer", related_name="components", on_delete=fields.OnDelete.CASCADE
    )

    class Meta:
        table = "consumer_component"


class ConsumerState(Model):
    id = fields.IntField(pk=True)

    mode: ConsumerMode = fields.CharEnumField(
        ConsumerMode, max_length=16, default=ConsumerMode.DISABLED
    )
    status: ConsumerStatus = fields.CharEnumField(
        ConsumerStatus, max_length=16, default=ConsumerStatus.STOPPED
    )
    started_at = fields.DatetimeField(auto_now_add=True)
    current_consumption = fields.SmallIntField(
        default=0,
        description="Current total consumer consumption. Important for MCCs. ",
    )

    consumer: fields.OneToOneRelation["Consumer"] = fields.OneToOneField(
        "models.Consumer", related_name="state", on_delete=fields.OnDelete.CASCADE
    )

    class Meta:
        table = "consumer_state"


class ConsumerRuntime(Model):
    id = fields.IntField(pk=True)

    date = fields.DateField()
    runtime = fields.SmallIntField()

    consumer: fields.ForeignKeyRelation["Consumer"] = fields.ForeignKeyField(
        "models.Consumer", related_name="runtimes", on_delete=fields.OnDelete.CASCADE
    )

    class Meta:
        table = "consumer_runtime"


Consumer_Pydantic = pydantic_model_creator(Consumer, name="Consumer")
ConsumerIn_Pydantic = pydantic_model_creator(Consumer, name="ConsumerIn")
ConsumerOut_Pydantic = pydantic_model_creator(Consumer, name="ConsumerOut")
