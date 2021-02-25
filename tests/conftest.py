import pytest
from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from exporter import util


@pytest.fixture
def client():
    app = Flask(__name__)

    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/health": util.health})

    client = app.test_client()

    yield client
