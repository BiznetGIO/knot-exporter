import logging
import os
from distutils.util import strtobool

from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from prometheus_client.core import REGISTRY

from exporter.collector import KnotCollector
from exporter import util

# setup log
logging.basicConfig(level="DEBUG")


# true/false from YAML can't be parsed automatically,
# thus `strtobool` is needed
# strtobool produce 0 or 1, so it still need to be wrapped by `bool`
knot_library_path = os.environ.get("KNOT_EXPORTER_LIBRARY_PATH", "libknot.so")
knot_socket_path = os.environ.get("KNOT_EXPORTER_SOCKET_PATH", "/run/knot/knot.sock")
knot_socket_timeout = int(os.environ.get("KNOT_EXPORTER_SOCKET_TIMEOUT", 2000))


def get_str_env(env_name):
    return bool(strtobool(os.environ.get(f"{env_name}", "true")))


collect_meminfo = get_str_env("KNOT_EXPORTER_COLLECT_MEMINFO")
collect_global_stats = get_str_env("KNOT_EXPORTER_COLLECT_GLOBAL_STATS")
collect_zone_stats = get_str_env("KNOT_EXPORTER_COLLECT_ZONE_STATS")
collect_zone_status = get_str_env("KNOT_EXPORTER_COLLECT_ZONE_STATUS")
collect_zone_read = get_str_env("KNOT_EXPORTER_COLLECT_ZONE_READ")

logging.info(
    f"KNOT_EXPORTER_SOCKET_TIMEOUT = {knot_socket_timeout}\n"
    f"KNOT_EXPORTER_COLLECT_MEMINFO = {collect_meminfo}\n"
    f"KNOT_EXPORTER_COLLECT_GLOBAL_STATS = {collect_global_stats}\n"
    f"KNOT_EXPORTER_COLLECT_ZONE_STATS = {collect_zone_stats}\n"
    f"KNOT_EXPORTER_COLLECT_ZONE_STATUS = {collect_zone_status}\n"
    f"KNOT_EXPORTER_COLLECT_ZONE_READ = {collect_zone_read}"
)

REGISTRY.register(
    KnotCollector(
        knot_library_path,
        knot_socket_path,
        knot_socket_timeout,
        collect_meminfo,
        collect_global_stats,
        collect_zone_stats,
        collect_zone_status,
        collect_zone_read,
    )
)

app = Flask(__name__)


app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app, {"/metrics": make_wsgi_app(), "/health": util.health}
)
