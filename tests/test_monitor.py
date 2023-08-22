from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_health_monitor import HealthMonitor


def test_that_health_monitor_has_all_expected_properties():
    # GIVEN FastAPI app
    app = FastAPI(debug=True)

    # GIVEN health monitor instance
    monitor = HealthMonitor(
        root_app=app,
        service_id="foobar",
        version="1",
        release_id="1.0.0",
        description="some description",
        extra_notes=["foonote"],
    )

    # WHEN fetching health status
    with TestClient(app) as client:
        res = client.get("/health")

    # THEN expect HTTP OK
    assert res.status_code == 200

    # THEN expect properties
    assert res.json()["service_id"] == monitor.service_id
    assert res.json()["version"] == monitor.version
    assert res.json()["release_id"] == monitor.release_id
    assert res.json()["description"] == monitor.description
    assert monitor.extra_notes[0] in res.json()["notes"]

    # THEN expect status
    assert res.json()["status"] == "ok"


def test_that_health_monitor_has_system_checks():
    # GIVEN FastAPI app
    app = FastAPI(debug=True)

    # GIVEN health monitor instance
    monitor = HealthMonitor(
        root_app=app,
        service_id="foobar",
        version="1",
        release_id="1.0.0",
        description="some description",
        extra_notes=["foonote"],
    )

    # WHEN fetching health status
    with TestClient(app) as client:
        res = client.get("/health")

    # THEN expect uptime check
    assert "uptime" in res.json()["checks"]

    # THEN expect observed unit in seconds
    assert res.json()["checks"]["uptime"]["observed_unit"] == "s"

    # THEN expect observed value to be float
    assert isinstance(res.json()["checks"]["uptime"]["observed_value"], float)
