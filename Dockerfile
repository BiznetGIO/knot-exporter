FROM python:3.7-slim-buster

# working with timezones
RUN apt-get install -y tzdata

WORKDIR /exporter

COPY ./requirements.txt /exporter/requirements.txt
RUN pip3 install -r /exporter/requirements.txt

COPY . /exporter

ENV PYTHONPATH '/exporter'
CMD ["gunicorn", "exporter.main:app",  "-b", ":9100"]
