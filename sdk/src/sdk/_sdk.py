from typing import Final

from cotc_common.metrics import MetricSnapshotJson
from requests import post
from requests.exceptions import ConnectionError as RequestConnectionError
from requests.models import Response
from json import dumps

JSON_HEADER: Final[dict[str, str]] = {"Content-Type": "application/json"}


def send_snapshots(*snapshots: MetricSnapshotJson, endpoint: str) -> Response | None:
    """
    Send a list of metric snapshots to the given API endpoint via POST request.

    Args:
        snapshots (MetricSnapshotJson): List of metric snapshots.
        endpoint (str): Endpoint to send the snapshots to.

    Returns:
        requests.Response | None: Server response or `None` if the connection failed.
    """

    try:
        return post(
            url=endpoint,
            headers=JSON_HEADER,
            json=dumps([s.model_dump() for s in snapshots]),

            timeout=10,
        )
    except RequestConnectionError:
        return None
