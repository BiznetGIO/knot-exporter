import os
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from prometheus_client.core import REGISTRY

from exporter.collector import KnotCollector
from exporter import util

knot_library_path = os.environ.get("KNOT_EXPORTER_LIBRARY_PATH", "libknot.so")
knot_socket_path = os.environ.get("KNOT_EXPORTER_SOCKET_PATH", "/run/knot/knot.sock")
knot_socket_timeout = os.environ.get("RESTKNOT_KNOT_LIB", 2000)
no_meminfo = False
no_global_stats = False
no_zone_stats = False
no_zone_status = False
no_zone_read = False

REGISTRY.register(
    KnotCollector(
        knot_library_path,
        knot_socket_path,
        knot_socket_timeout,
        no_meminfo,
        no_global_stats,
        no_zone_stats,
        no_zone_status,
        no_zone_read,
    )
)

app = Flask(__name__)


app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app, {"/metrics": make_wsgi_app(), "/health": util.health}
)
