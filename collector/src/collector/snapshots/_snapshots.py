from socket import gethostname
from typing import TYPE_CHECKING, Any

import requests
from cotc_common.metrics import DeviceJson, MetricJson, MetricSnapshotJson
from cotc_common.util import utc_now
from psutil import cpu_percent, virtual_memory

from collector.config import Config

if TYPE_CHECKING:
    from requests import Response


def local_snapshot() -> MetricSnapshotJson:
    """Retrieve a snapshot of the local machine's CPU and RAM usage."""

    # CPU % usage (1 sec. interval)
    cpu_usage: MetricJson = MetricJson(
        name="CPU Usage",
        value=cpu_percent(interval=1),
        unit="%",
    )

    # RAM usage (in MB)
    ram_usage: MetricJson = MetricJson(
        name="RAM Usage",
        value=virtual_memory().used / 1e6,
        unit="MB",
    )

    return MetricSnapshotJson(
        device=DeviceJson(name=gethostname()),
        timestamp=utc_now().isoformat(),
        metrics=[cpu_usage, ram_usage],
    )


def remote_snapshot(config: Config) -> MetricSnapshotJson:
    """Retrieve a snapshot of weather data from a remote weather API."""

    url: str = config.app.weather_endpoint.format(
        city=config.app.city,
        api_key=config.app.api_key,
    )

    response: Response = requests.get(url, timeout=10)
    data: Any = response.json()

    temp: float = float(data["main"]["temp"])
    humidity: float = float(data["main"]["humidity"])

    temperature: MetricJson = MetricJson(
        name="Temperature",
        value=temp,
        unit="°C",
    )

    humidity_metric: MetricJson = MetricJson(
        name="Humidity",
        value=humidity,
        unit="%",
    )

    return MetricSnapshotJson(
        device=DeviceJson(name=f"OpenWeather:{config.app.city}"),
        timestamp=utc_now().isoformat(),
        metrics=[temperature, humidity_metric],
    )
