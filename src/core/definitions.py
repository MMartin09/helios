from enum import Enum


class ConsumerStatus(str, Enum):
    STOPPED = "STOPPED"
    PARTIAL_RUNNING = "PARTIAL_RUNNING"
    RUNNING = "RUNNING"


class ConsumerMode(str, Enum):
    DISABLED = "DISABLED"
    AUTOMATIC = "AUTOMATIC"
    HAND_ON = "HAND_ON"
    HAND_OFF = "HAND_OFF"


class GridMode(str, Enum):
    NOT_SET = "NOT_SET"
    FEED_IN = "FEED_IN"
    CONSUME = "CONSUME"
