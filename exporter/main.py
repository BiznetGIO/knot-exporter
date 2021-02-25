from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from prometheus_client.core import REGISTRY

from exporter.collector import KnotCollector
from exporter import util


REGISTRY.register(KnotCollector())

app = Flask(__name__)


app.wsgi_app = DispatcherMiddleware(
    app.wsgi_app, {"/metrics": make_wsgi_app(), "/health": util.health}
)
