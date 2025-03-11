from __future__ import annotations

from datetime import datetime as dt
from typing import TYPE_CHECKING

from pydantic import BaseModel, ValidationError

if TYPE_CHECKING:
    from cotc_common.types import JSONObj


class MetricJson(BaseModel):
    """
    Single metric JSON.
    """

    name: str
    value: float
    unit: str


class MetricSchema(BaseModel):
    """
    Single metric schema.
    """

    name: str
    value: float
    unit: str
    snapshot_id: int


class DeviceJson(BaseModel):
    """
    Device JSON.
    """

    name: str


class DeviceSchema(BaseModel):
    """
    Device schema.
    """

    name: str


class MetricSnapshotJson(BaseModel):
    """
    Metric snapshot JSON (collection of single metrics).
    """

    device: DeviceJson
    timestamp: str
    metrics: list[MetricJson]


class MetricSnapshotSchema(BaseModel):
    """
    Metric snapshot schema.
    """

    device_id: int
    timestamp: dt
    metrics: list[MetricSchema]


def parse_snapshot_json(json: JSONObj) -> MetricSnapshotJson | None:
    """
    Parse raw JSON into MetricSnapshotJson object.

    Args:
        json (JSONObj): Raw JSON.

    Returns:
        MetricSnapshotJson | None: Snapshot JSON object or None if invalid format.
    """

    try:
        return MetricSnapshotJson(**json)
    except ValidationError:
        return None
