<div align="center">
<h1>knot-exporter</h1>

Export Knot info to Prometheus

<a href="https://github.com/BiznetGIO/knot-exporter/actions/workflows/ci.yml">
<img src="https://github.com/BiznetGIO/knot-exporter/workflows/ci/badge.svg">
</a>

<p></p>

</div>

---


*knot-exporter* is a Prometheus exporter for [Knot](https://www.knot-dns.cz/)'s server and query statistics.

## Features

- Uses a real webserver.
- `Health` endpoint containing build version and status.
- Dockerized

## Usage

Run as usual `docker` applications.

See [docker-compose.example.yml](docker-compose.example.yml) for detailed options.

Visit `http://localhost:9100/metrics` to view the metrics, and `/health` to check its status.


---

## Licence

`knot-exporter` source code is licensed under the [GPL-3.0 License](https://choosealicense.com/licenses/gpl-3.0/). Because it is a derivative work of `Knot`.

`knot-exporter` is based on [Alessandro Ghedini's knot-exporter](https://github.com/ghedo/knot_exporter)

The Python bindings for libknot were taken from the official [Knot repo](https://github.com/CZ-NIC/knot/tree/master/python/libknot) [GPL-3.0 Licensed].

