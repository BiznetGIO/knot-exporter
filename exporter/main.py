import os
import http.server
from prometheus_client.core import REGISTRY
from prometheus_client.exposition import MetricsHandler

from exporter.collector import KnotCollector


def main():
    exporter_addr = os.environ.get("KNOT_EXPORTER_ADDR", "0.0.0.0")
    exporter_port = os.environ.get("KNOT_EXPORTER_PORT", 9100)

    REGISTRY.register(KnotCollector())

    httpd = http.server.HTTPServer((exporter_addr, int(exporter_port)), MetricsHandler)

    httpd.serve_forever()


if __name__ == "__main__":
    main()
