from logging import CRITICAL, ERROR, INFO, Logger, getLogger
from time import sleep
from typing import TYPE_CHECKING, Any, Self

from cotc_common.util import ExitCode, PublisherRank, clear_scr
from requests.status_codes import codes as status_codes
from sdk import send_snapshots

from collector.config import Config, init_config
from collector.snapshots import local_snapshot, remote_snapshot

if TYPE_CHECKING:
    from cotc_common.metrics import MetricSnapshotJson
    from requests import Response


class App:
    config: Config
    interval: float
    number: int
    logger: Logger

    def __init__(self: Self) -> None:
        self.config = init_config()
        self.interval = self.config.argv.interval
        self.number = self.config.argv.number
        self.logger = getLogger(__name__)

    def run(self: Self) -> int:
        ret: ExitCode = ExitCode.SUCCESS

        fmt: str = "%.0f" if self.interval.is_integer() else "%.2f"
        clear_scr()
        self.logger.info(
            "Collector program started (number: <fly>%d*</fly>, interval: <fly>%ss</fly>)",
            self.number,
            fmt % self.interval,
        )
        print()

        def loop_log(level: int, msg: str, *args: Any) -> None:
            msg = f"[<fly>{i=}</fly>/<fly>{self.number}</fly>] {msg}"
            if args:
                self.logger.log(level, msg, *args)
            else:
                self.logger.log(level, msg)

        remote_rank: PublisherRank | None = None
        local_rank: PublisherRank | None = None

        try:
            for i in range(1, self.number + 1):
                loop_log(INFO, "Sending metrics")

                remote: MetricSnapshotJson = remote_snapshot(self.config)
                local: MetricSnapshotJson = local_snapshot()

                response: Response | None = send_snapshots(
                    local,
                    remote,
                    endpoint=self.config.argv.endpoint,
                )

                if response is None:
                    loop_log(CRITICAL, "Connection refused")
                    ret = ExitCode.CONNECTION_REFUSED
                    print()
                    break

                ok: bool = False
                code: int = response.status_code
                match code:
                    case status_codes.OK:
                        loop_log(INFO, "Metrics sent successfully")
                        ok = True
                    case _:
                        loop_log(ERROR, "Failed to send metrics: %d", code)

                if ok:
                    new_rank_str_remote: str = response.json()[remote.device.name]
                    new_rank_remote: PublisherRank = PublisherRank[new_rank_str_remote]
                    new_rank_str_local: str = response.json()[local.device.name]
                    new_rank_local: PublisherRank = PublisherRank[new_rank_str_local]

                    if remote_rank is None:
                        remote_rank = new_rank_remote
                        self.logger.info(
                            "Current rank for <flg>%s</flg> is **<flg>%s</flg>**",
                            remote.device.name,
                            remote_rank.name,
                        )
                    elif new_rank_remote.value == remote_rank.next.value:
                        remote_rank = new_rank_remote
                        self.logger.info(
                            "Device <flg>%s</flg> is now a **<flg>%s</flg>** level publisher ... WOW!",
                            remote.device.name,
                            remote_rank.name,
                        )

                    if local_rank is None:
                        local_rank = new_rank_local
                        self.logger.info(
                            "Current rank for <flg>%s</flg> is **<flg>%s</flg>**",
                            local.device.name,
                            local_rank.name,
                        )
                    elif new_rank_local.value == local_rank.next.value:
                        local_rank = new_rank_local
                        self.logger.info(
                            "Device <flg>%s</flg> is now a **<flg>%s</flg>** level publisher ... WOW!",
                            local.device.name,
                            local_rank.name,
                        )
                if i < self.number:
                    sleep(self.interval)
                print()
            else:
                self.logger.info("All <fly>%d</fly> iterations completed", self.number)

        except KeyboardInterrupt:
            print("\r", end="")  # Hide "^C"
            self.logger.exception("Keyboard interrupt received")
            ret = ExitCode.INTERRUPTED
            print()

        self.logger.info(
            "Collector program finished with exit code <fly>%d</fly> (<fly>%s</fly>)",
            ret,
            ret.name,
        )
        return ret.value
