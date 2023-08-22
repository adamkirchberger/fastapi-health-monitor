import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_health_monitor import HealthMonitor, HealthStatus
from fastapi_health_monitor.settings import settings


@pytest.mark.parametrize("component_status", [HealthStatus.OK, "ok"])
def test_that_health_monitor_component_is_registered(component_status):
    # GIVEN FastAPI app
    app = FastAPI(debug=True)

    # GIVEN health check interval
    settings.heath_check_delay_seconds = 1

    # GIVEN component check function
    def fake_component_check(component):
        component.status = component_status
        return component

    # GIVEN health monitor instance
    monitor = HealthMonitor(
        root_app=app,
        service_id="foobar",
        version="1",
        release_id="1.0.0",
        description="some description",
        extra_notes=["foonote"],
    )

    # GIVEN registered component
    monitor.add_component(
        component_name="fake_component",
        measurement_name="foobar",
        component_type="footype",
        check_function=fake_component_check,
        observed_unit="foounit",
    )

    # WHEN fetching health status
    with TestClient(app) as client:
        res = client.get("/health")

    # THEN expect OK
    assert res.status_code == 200

    # THEN expect component to be present in checks
    assert "fake_component:foobar" in res.json()["checks"]

    # THEN expect component to be ok
    assert res.json()["checks"]["fake_component:foobar"]["status"] == "ok"


@pytest.mark.parametrize(
    "component_status", [HealthStatus.ERROR, "error", HealthStatus.UNKNOWN]
)
def test_that_health_monitor_unhealthy_component_returns_error_status(component_status):
    # GIVEN FastAPI app
    app = FastAPI(debug=True)

    # GIVEN health check interval
    settings.heath_check_delay_seconds = 1

    # GIVEN component check function
    def fake_component_check(component):
        component.status = component_status
        return component

    # GIVEN health monitor instance
    monitor = HealthMonitor(
        root_app=app,
        service_id="foobar",
        version="1",
        release_id="1.0.0",
        description="some description",
        extra_notes=["foonote"],
    )

    # GIVEN registered component
    monitor.add_component(
        component_name="fake_component",
        measurement_name="foobar",
        component_type="footype",
        check_function=fake_component_check,
        observed_unit="foounit",
    )

    # WHEN fetching health status
    with TestClient(app) as client:
        res = client.get("/health")

    # THEN expect unavailable
    assert res.status_code == 503

    # THEN expect status
    assert res.json()["status"] == "error"

    # THEN expect component to be present in checks
    assert "fake_component:foobar" in res.json()["checks"]


def test_that_health_monitor_component_error_returns_error_status(caplog):
    # GIVEN FastAPI app
    app = FastAPI(debug=True)

    # GIVEN health check interval
    settings.heath_check_delay_seconds = 1

    # GIVEN component check function that raises error
    def fake_component_check(component):
        raise RuntimeError("forced error")

    # GIVEN health monitor instance
    health_monitor = HealthMonitor(
        root_app=app,
        service_id="foobar",
        version="1",
        release_id="1.0.0",
        description="some description",
        extra_notes=["foonote"],
    )

    # GIVEN registered component
    health_monitor.add_component(
        component_name="fake_component",
        measurement_name="foobar",
        component_type="footype",
        check_function=fake_component_check,
        observed_unit="foounit",
    )

    # WHEN fetching health status
    with TestClient(app) as client:
        res = client.get("/health")

    # THEN expect unavailable
    assert res.status_code == 503

    # THEN expect status
    assert res.json()["status"] == "error"

    # THEN expect component to be present in checks
    assert "fake_component:foobar" in res.json()["checks"]

    # THEN expect component to be error status
    assert res.json()["checks"]["fake_component:foobar"]["status"] == "error"

    # THEN expect component output message
    assert (
        res.json()["checks"]["fake_component:foobar"]["output"]
        == "Failed to run component health check function."
    )

    # THEN expect component error detail in logs
    assert "RuntimeError: forced error" in caplog.text
