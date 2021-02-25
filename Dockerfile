FROM python:3.7-slim-buster

# working with timezones
RUN apt-get install -y tzdata

WORKDIR /exporter

COPY ./requirements.txt /exporter/requirements.txt
RUN pip3 install -r /exporter/requirements.txt

ARG BUILD_VERSION
RUN echo "$BUILD_VERSION"
RUN echo "$BUILD_VERSION" > build-version.txt

COPY . /exporter
RUN cat /exporter/build-version.txt

ENV PYTHONPATH '/exporter'
CMD ["gunicorn", "exporter.main:app",  "-b", ":9100"]
