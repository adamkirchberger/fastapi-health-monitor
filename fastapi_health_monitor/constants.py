from enum import Enum


class HealthStatus(Enum):
    """
    Health status choices.
    """

    OK = "ok"
    ERROR = "error"
    STARTING_UP = "starting_up"
    SHUTTING_DOWN = "shutting_down"
    UNKNOWN = "unknown"


class ComponentType(Enum):
    """
    Health check component type.
    """

    COMPONENT = "component"
    DATASTORE = "datastore"
    SYSTEM = "system"
