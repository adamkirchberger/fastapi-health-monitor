# FastAPI Health Monitor

[![codecov](https://codecov.io/gh/adamkirchberger/fastapi-health-monitor/graph/badge.svg?token=8IdTKDXy89)](https://codecov.io/gh/adamkirchberger/fastapi-health-monitor)

A health monitor for FastAPI applications which runs user provided background checks to determine the current overall health status of an API system.

## Features

* Microservices architecture health endpoint.
* Returns HTTP status codes. (200 OK / 503 unavailable)
* Can be used for Kubernetes liveness / readiness checks.
* Supports custom dependency and subcomponent checks.
  * Simple ok/error checks or optional support for more detailed metrics.

## Installation

Install using the pip package manager.

```
pip install fastapi-health-monitor
```

## Usage

This example shows a FastAPI application which returns a dad joke from an external API.

The checks are run every 10 seconds by default. This can be changed using an environment variable `HEALTH_CHECK_DELAY_SECONDS`.

```python
from fastapi import FastAPI
import requests

# Import health monitor
from fastapi_health_monitor import HealthMonitor, ComponentHealth, HealthStatus


app = FastAPI()

# Create health monitor instance
monitor = HealthMonitor(
    root_app=app,
    service_id="dadjokes",
    version="1",
    release_id="1.0.0",
    extra_notes=["environment=test"],
    health_endpoint="/health",
)

# Create a component check function
def check_external_api(component: ComponentHealth):
    """
    Check that external API returns 200 OK
    """
    res = requests.get(
        "https://icanhazdadjoke.com/", headers={"Accept": "application/json"}
    )

    # Update status based on status code
    if res.status_code == 200:
        component.status = HealthStatus.OK
    else:
        component.status = HealthStatus.ERROR

    return component


# Add a component to the health monitor
monitor.add_component(
    component_name="icanhazdadjoke.com",
    measurement_name="reachability",
    check_function=check_external_api,
)


@app.get("/")
async def root():
    """
    Return a dad joke from https://icanhazdadjoke.com/
    """
    return (
        requests.get(
            "https://icanhazdadjoke.com/", headers={"Accept": "application/json"}
        )
        .json()
        .get("joke")
    )

```

## Example response

```json
{
    "service_id": "dadjokes",
    "status": "ok",
    "version": "1",
    "release_id": "1.0.0",
    "notes": [
        "startup_timestamp=2023-08-22T18:02:55.133246",
        "last_checked_timestamp=2023-08-22T18:03:06.617896",
        "environment=test"
    ],
    "checks": {
        "icanhazdadjoke.com:reachability": {
            "component_name": "icanhazdadjoke.com",
            "measurement_name": "reachability",
            "status": "ok",
            "time": "2023-08-22T18:03:06.617719"
        },
        "uptime": {
            "measurement_name": "uptime",
            "component_type": "system",
            "observed_value": 11.484558,
            "observed_unit": "s",
            "status": "ok",
            "time": "2023-08-22T18:03:06.617811"
        }
    }
}
```

## Authors

FastAPI Health Monitor was created by Adam Kirchberger in 2023.

## License

MIT

See [LICENSE](https://github.com/adamkirchberger/fastapi-health-monitor/blob/main/LICENSE).

## Change Log

See [CHANGELOG](https://github.com/adamkirchberger/fastapi-health-monitor/blob/main/CHANGELOG.md)