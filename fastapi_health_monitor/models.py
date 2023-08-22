from typing import Optional, List, Dict, Union
from pydantic import BaseModel, Field

from .constants import HealthStatus, ComponentType


class ComponentHealth(BaseModel):
    """
    Represents the health status of a logical downstream dependency or sub-component.
    """

    component_name: Optional[str] = Field(
        default=None, title="Human-readable name for the component."
    )
    measurement_name: Optional[str] = Field(
        default=None,
        title="Name of the measurement type that the status is reported for.",
    )
    component_id: Optional[str] = Field(
        default=None,
        title="Unique identifier of an instance of a specific sub-component/dependency of a service.",
    )
    component_type: Optional[Union[str, ComponentType]] = Field(
        default=None,
        title="Type of the component and could be one of: component, datastore, system",
    )
    observed_value: Optional[Union[str, int, float, dict, list]] = Field(
        default=None,
        title="Any valid JSON value, such as: string, number, object, array or literal.",
    )
    observed_unit: Optional[str] = Field(
        default=None,
        title="Clarifies the unit of measurement in which observed_unit is reported.",
    )
    status: HealthStatus = Field(
        default=HealthStatus.UNKNOWN,
        title="Indicates whether the component status is acceptable or not.",
    )
    time: Optional[str] = Field(
        default=None,
        title="The date-time, in ISO8601 format, at which the reading of the observedValue was recorded.",
    )
    output: Optional[str] = Field(
        default=None, title='Raw error output, in case of "fail" or "warn" states.'
    )


class SystemHealth(BaseModel):
    """
    Represents the overall health status of the API system.
    """

    service_id: Optional[str] = Field(
        default=None,
        title="Unique identifier of the service, in the application scope.",
    )
    status: HealthStatus = Field(
        title="Indicates whether the service status is acceptable or not."
    )
    version: Optional[str] = Field(
        default=None,
        title="Public version of the service, normally the major version.",
    )
    release_id: Optional[str] = Field(
        default=None,
        title="Internal version of the service. Can be commit hash or semantic version.",
    )
    description: Optional[str] = Field(
        default=None,
        title="Human-friendly description of the service.",
    )
    notes: List[str] = Field(
        default_factory=list,
        title="Array of notes relevant to the current state of health.",
    )
    output: Optional[str] = Field(
        default=None, title='Raw error output, in case of "fail" or "warn" states.'
    )
    checks: Dict[str, ComponentHealth] = Field(
        default={},
        title=(
            "Provides detailed health statuses of additional downstream systems "
            "and endpoints which can affect the overall health of the main API."
        ),
    )
