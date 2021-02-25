import json
import pathlib


def read_file(other_file_name, filename):
    root_dir = pathlib.Path(other_file_name).resolve().parent
    path = root_dir.joinpath(filename)

    if path.is_file():
        with open(path, "rb") as f:
            content = f.read().decode("utf-8")
            return content


def read_version(other_file_name, filename):
    """Read the the current version or build of the app"""
    version = ""

    version = read_file(other_file_name, filename)
    if version:
        version = version.rstrip()

    if not version:
        version = "__UNKNOWN__"

    return version


def health(environ, start_response):
    headers = [("content-type", "application/json")]
    status = "200 OK"

    build = read_version("requirements.txt", "build-version.txt")
    output = json.dumps({"data": {"status": "running", "build": build}})
    output_encoded = output.encode("utf-8")

    start_response(status, headers)
    return [output_encoded]
