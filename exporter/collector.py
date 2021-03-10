import psutil
import re
from subprocess import check_output
from prometheus_client.core import GaugeMetricFamily

from exporter.vendor.libknot.control import load_lib, KnotCtl


def memory_usage():
    out = dict()
    pids = check_output(["pidof", "knotd"]).split(b" ")
    for pid in pids:
        if not pid:
            continue
        key = int(pid)
        out[key] = psutil.Process(key).memory_info()._asdict()["rss"]
    return out


class KnotCollector(object):
    def __init__(
        self,
        lib,
        sock,
        ttl,
        collect_meminfo: bool,
        collect_stats: bool,
        collect_zone_stats: bool,
        collect_zone_status: bool,
        collect_zone_read: bool,
    ):
        load_lib(lib)
        self._sock = sock
        self._ttl = ttl
        self.collect_meminfo = collect_meminfo
        self.collect_stats = collect_stats
        self.collect_zone_stats = collect_zone_stats
        self.collect_zone_status = collect_zone_status
        self.collect_zone_read = collect_zone_read

    def convert_state_time(time):

        if time == "pending" or time == "running":
            return 0
        elif time == "not scheduled":
            return None
        else:
            match = re.match("([+-])((\d+)D)?((\d+)h)?((\d+)m)?((\d+)s)?", time)
            seconds = -1 if match.group(1) == "-" else 1
            if match.group(3):
                seconds = seconds + 86400 * int(match.group(3))
            if match.group(5):
                seconds = seconds + 3600 * int(match.group(5))
            if match.group(7):
                seconds = seconds + 60 * int(match.group(7))
            if match.group(9):
                seconds = seconds + int(match.group(9))

        return seconds

    def collect(self):
        ctl = KnotCtl()
        ctl.connect(self._sock)
        ctl.set_timeout(self._ttl)

        if self.collect_meminfo:
            # Get global metrics.
            for pid, usage in memory_usage().items():
                m = GaugeMetricFamily(
                    "knot_memory_usage", "", labels=["section", "type"]
                )
                m.add_metric(["server", str(pid)], usage)
                yield m

        if self.collect_stats:
            ctl.send_block(cmd="stats", flags="")
            global_stats = ctl.receive_stats()

            for section, section_data in global_stats.items():
                for item, item_data in section_data.items():
                    name = ("knot_" + item).replace("-", "_")
                    try:
                        for kind, kind_data in item_data.items():
                            m = GaugeMetricFamily(name, "", labels=["section", "type"])
                            m.add_metric([section, kind], kind_data)
                            yield m
                    except AttributeError:
                        m = GaugeMetricFamily(name, "", labels=["section"])
                        m.add_metric([section], item_data)
                        yield m

        if self.collect_zone_stats:
            # Get zone metrics.
            ctl.send_block(cmd="zone-stats", flags="")
            zone_stats = ctl.receive_stats()

            if "zone" in zone_stats:
                for zone, zone_data in zone_stats["zone"].items():
                    for section, section_data in zone_data.items():
                        for item, item_data in section_data.items():
                            name = ("knot_" + item).replace("-", "_")
                            try:
                                for kind, kind_data in item_data.items():
                                    m = GaugeMetricFamily(
                                        name, "", labels=["zone", "section", "type"]
                                    )
                                    m.add_metric([zone, section, kind], kind_data)
                                    yield m
                            except AttributeError:
                                m = GaugeMetricFamily(
                                    name, "", labels=["zone", "section"]
                                )
                                m.add_metric([zone, section], item_data)
                                yield m

        if self.collect_zone_status:
            # zone state metrics
            ctl.send_block(cmd="zone-status")
            zone_states = ctl.receive_block()

            for zone, info in zone_states.items():
                metrics = ["expiration", "refresh"]

                for metric in metrics:
                    seconds = KnotCollector.convert_state_time(info[metric])
                    if seconds == None:
                        continue

                    m = GaugeMetricFamily(
                        "knot_zone_stats_" + metric, "", labels=["zone"]
                    )
                    m.add_metric([zone], seconds)

                    yield m

        if self.collect_zone_read:
            # zone configuration metrics
            ctl.send_block(cmd="zone-read", rtype="SOA")
            zones = ctl.receive_block()

            for name, params in zones.items():
                metrics = [
                    {"name": "knot_zone_refresh", "index": 3},
                    {"name": "knot_zone_retry", "index": 4},
                    {"name": "knot_zone_expiration", "index": 5},
                ]

                zone_config = params[name]["SOA"]["data"][0].split(" ")

                for metric in metrics:
                    m = GaugeMetricFamily(metric["name"], "", labels=["zone"])
                    m.add_metric([name], int(zone_config[metric["index"]]))

                    yield m
