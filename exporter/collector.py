import os
from prometheus_client.core import GaugeMetricFamily


from exporter.vendor.libknot import control as knotlib


def connect_knot():
    knot_library_path = os.environ.get("KNOT_EXPORTER_LIBRARY_PATH", "libknot.so")
    knot_socket_path = os.environ.get(
        "KNOT_EXPORTER_SOCKET_PATH", "/run/knot/knot.sock"
    )
    knot_socket_timeout = os.environ.get("RESTKNOT_KNOT_LIB", 2000)

    knotlib.load_lib(knot_library_path)
    knot_ctl = knotlib.KnotCtl()

    try:
        knot_ctl.connect(knot_socket_path)
        knot_ctl.set_timeout(knot_socket_timeout)
        return knot_ctl
    except knotlib.KnotCtlError as e:
        raise ValueError(f"Can't connect to knot socket: {e}")


class KnotCollector(object):
    def collect(self):
        ctl = connect_knot()

        # Get global metrics.
        ctl.send_block(cmd="stats", flags="F")
        global_stats = ctl.receive_stats()

        for section, section_data in global_stats.items():
            for item, item_data in section_data.items():
                name = ("knot_" + section + "_" + item).replace("-", "_")
                yield GaugeMetricFamily(name, "", value=item_data)

        # Get zone metrics.
        ctl.send_block(cmd="zone-stats", flags="F")
        zone_stats = ctl.receive_stats()

        if "zone" in zone_stats:
            for zone, zone_data in zone_stats["zone"].items():
                for section, section_data in zone_data.items():
                    for item, item_data in section_data.items():
                        for kind, kind_data in item_data.items():
                            if kind_data == 0:
                                continue

                            name = ("knot_" + item).replace("-", "_")
                            m = GaugeMetricFamily(
                                name, "", labels=["zone", "section", "type"]
                            )
                            m.add_metric([zone, section, kind], kind_data)
                            yield m
