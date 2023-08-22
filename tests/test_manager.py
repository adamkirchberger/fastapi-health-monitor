import logging
import asyncio
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from fastapi_health_monitor import HealthMonitor
from fastapi_health_monitor.manager import HealthCheckManager


def test_that_health_manager_loop_exits_when_app_terminates(caplog):
    # GIVEN log level
    caplog.set_level(logging.DEBUG)

    # GIVEN FastAPI app
    app = FastAPI(debug=True)

    # GIVEN mock manager instance
    mock_manager = HealthCheckManager(
        service_id="foobar",
        version="1",
        release_id="1.0.0",
        description="some description",
        extra_notes=["foonote"],
    )

    # GIVEN update checks has been mocked to raise the exit exception
    mock_manager._update_checks = AsyncMock(side_effect=asyncio.CancelledError)

    with patch(
        "fastapi_health_monitor.healthmonitor.HealthCheckManager",
        return_value=mock_manager,
    ):
        # GIVEN health monitor instance is created
        HealthMonitor(
            root_app=app,
            service_id=mock_manager.service_id,
            version=mock_manager.version,
            release_id=mock_manager.release_id,
            description=mock_manager.description,
            extra_notes=mock_manager.extra_notes,
        )

    # WHEN fetching health status
    with TestClient(app) as client:
        client.get("/health")

    # THEN expect log message
    assert "stopped health check refresh" in caplog.text


def test_that_health_manager_logs_exceptions(caplog):
    # GIVEN log level
    caplog.set_level(logging.DEBUG)

    # GIVEN FastAPI app
    app = FastAPI(debug=True)

    # GIVEN mock manager instance
    mock_manager = HealthCheckManager(
        service_id="foobar",
        version="1",
        release_id="1.0.0",
        description="some description",
        extra_notes=["foonote"],
    )

    # GIVEN update checks has been mocked to raise an exception
    mock_manager._update_checks = AsyncMock(side_effect=RuntimeError("forced error"))

    with patch(
        "fastapi_health_monitor.healthmonitor.HealthCheckManager",
        return_value=mock_manager,
    ):
        # GIVEN health monitor instance is created
        HealthMonitor(
            root_app=app,
            service_id=mock_manager.service_id,
            version=mock_manager.version,
            release_id=mock_manager.release_id,
            description=mock_manager.description,
            extra_notes=mock_manager.extra_notes,
        )

    # WHEN fetching health status
    with TestClient(app) as client:
        client.get("/health")

    # THEN expect log message
    assert "manager loop error: forced error" in caplog.text
