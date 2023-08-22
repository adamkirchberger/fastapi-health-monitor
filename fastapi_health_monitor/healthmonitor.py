import logging
from typing import Optional, List, Callable
from fastapi import FastAPI, APIRouter, Response, status

from .constants import HealthStatus
from .models import ComponentHealth, SystemHealth
from .manager import HealthCheckManager
from .checkrunner import CheckRunner


logger = logging.getLogger(__name__)
router = APIRouter()


class HealthMonitor:
    def __init__(
        self,
        root_app: FastAPI,
        service_id: str,
        version: str,
        release_id: str,
        description: Optional[str] = None,
        extra_notes: Optional[List[str]] = None,
        health_endpoint="/health",
    ) -> None:
        """
        A HealthMonitor which runs continuous background checks to determine API system health.

        Args:

            root_app (FastAPI): FastAPI root app instance.
            service_id (str): Unique identifier of the service.
            version (str): Public version of the service.
            release_id (str): Implementation version of the service.
            description (str): Optional human-friendly description of the service.
            extra_notes (list): Optional notes relevant to the service health.
            health_endpoint (str): Health endpoint. Default: /health
        """
        self._root_app = root_app
        self.service_id = service_id
        self.version = version
        self.release_id = release_id
        self.description = description
        self.extra_notes = extra_notes or []
        self.health_endpoint = health_endpoint

        # Attach monitor to app
        self._attach_to_app(root_app=root_app)

        # Create health check manager instance
        self._manager = HealthCheckManager(
            service_id=self.service_id,
            version=self.version,
            release_id=self.release_id,
            description=self.description,
            extra_notes=self.extra_notes,
        )

    def _attach_to_app(
        self,
        root_app: FastAPI,
    ):
        """
        Attach the monitor to the FastAPI root app.

        Args:
            root_app (FastAPI): FastAPI root app.
        """

        # Register events with root app
        @root_app.on_event("startup")
        async def startup_event() -> None:
            logger.info("service starting")
            await self._manager.start()

        @root_app.on_event("shutdown")
        async def shutdown_event() -> None:
            logger.info("service shutting down")
            self._manager.stop()

        @router.get(
            "",
            name="Get health status",
            response_model=SystemHealth,
            response_model_exclude_none=True,
            responses={
                200: {
                    "description": "The application is healthy.",
                    "model": SystemHealth,
                },
                503: {
                    "description": "The application is unhealthy.",
                    "model": SystemHealth,
                },
            },
        )
        @router.get(
            "/",
            include_in_schema=False,
            response_model_exclude_none=True,
        )
        async def _(response: Response) -> SystemHealth:
            """
            Returns current health status.
            """
            # Get response
            last_response = self._manager.get_response()

            # Determine HTTP status code
            response.status_code = (
                status.HTTP_200_OK
                if last_response.status == HealthStatus.OK
                else status.HTTP_503_SERVICE_UNAVAILABLE
            )
            logger.info(f"health status: {response.status_code}")

            return last_response

        # Add router into root app
        root_app.include_router(router, prefix=self.health_endpoint)

    def add_component(
        self,
        component_name: str,
        measurement_name: str,
        check_function: Callable[[ComponentHealth], ComponentHealth],
        component_type: str = None,
        observed_unit: Optional[str] = None,
        component_id: Optional[str] = None,
    ):
        """
        Add component to health monitor checks.

        Args:
            component_name (str): Human-readable name for the component.
            measurement_name (str): Name of the measurement type that the status is reported for.
            check_function (callable): Check function which receives one APIHealthComponent argument and returns it.
            component_type (str): Type of the component and could be one of: component, datastore, system.
            observed_unit (str): Clarifies the unit of measurement in which observed_unit is reported.
            component_id (str): Unique identifier of an instance of a specific sub-component/dependency of a service.
        """
        # Add component to service
        self._manager.add_check_runner(
            CheckRunner(
                component=ComponentHealth(
                    component_name=component_name,
                    measurement_name=measurement_name,
                    component_id=component_id,
                    component_type=component_type,
                    observed_unit=observed_unit,
                ),
                check_function=check_function,
            )
        )
        logger.info(f"added check runner: {component_name}:{measurement_name}")
