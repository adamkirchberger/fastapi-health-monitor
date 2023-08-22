import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime

from .settings import settings
from .models import SystemHealth, ComponentHealth
from .constants import HealthStatus
from .checkrunner import CheckRunner


logger = logging.getLogger(__name__)


class HealthCheckManager:
    def __init__(
        self,
        service_id: str,
        version: str,
        release_id: str,
        description: str = None,
        extra_notes: Optional[List[str]] = None,
    ):
        """
        Manages and executes checks to determine the system health.

        Args:
            service_id (str): Unique identifier of the service.
            version (str): Public version of the service.
            release_id (str): Implementation version of the service.
            description (str): Optional human-friendly description of the service.
            extra_notes (list): Optional notes relevant to the service health.
        """
        self.service_id = service_id
        self.version = version
        self.release_id = release_id
        self.description = description
        self.extra_notes = extra_notes = extra_notes or []

        self.status: HealthStatus = HealthStatus.UNKNOWN
        self.startup_timestamp: Optional[datetime] = None
        self.last_checked_timestamp: Optional[datetime] = None
        self.checks: Dict[str, ComponentHealth] = {}
        self.runners: List[CheckRunner] = []

    async def start(self) -> None:
        """
        Start the manager.
        """
        logger.info("starting health check manager")
        self.startup_timestamp = datetime.utcnow()
        self.status = HealthStatus.STARTING_UP

        # Run continuous checks
        loop = asyncio.get_running_loop()
        loop.create_task(self._run())

    def stop(self) -> None:
        """
        Stop the manager.
        """
        self.status = HealthStatus.SHUTTING_DOWN
        logger.info("stopped health check manager")

    async def _run(self) -> None:
        """
        Main health check loop.
        """
        while self.status != HealthStatus.SHUTTING_DOWN:
            try:
                await self._update_checks()
            except asyncio.CancelledError:
                # break when app is exited
                break
            except Exception as e:  # pylint: disable=W0718
                logger.exception("manager loop error: " + str(e))
            # Wait for health check delay
            await asyncio.sleep(settings.heath_check_delay_seconds)
        logger.info("stopped health check refresh")

    def get_response(self) -> SystemHealth:
        """
        Get current health check response.

        Returns:
            SystemHealth: health instance.
        """
        return SystemHealth(
            service_id=self.service_id,
            status=self.status,
            version=self.version,
            release_id=self.release_id,
            description=self.description,
            notes=[
                "startup_timestamp="
                + (
                    self.startup_timestamp.isoformat()
                    if self.startup_timestamp
                    else "unknown"
                ),
                "last_checked_timestamp="
                + (
                    self.last_checked_timestamp.isoformat()
                    if self.last_checked_timestamp
                    else "unknown"
                ),
            ]
            + self.extra_notes,
            checks=self.checks,
        )

    async def _update_checks(self) -> None:
        """
        Update health checks.
        """
        check_results: List[ComponentHealth] = []
        # Loop all runners
        for runner in self.runners:
            # Run check and store response
            response = await runner.run_check()
            check_results.append(response)

        # Determine system status
        self.status = (
            HealthStatus.ERROR
            if any(HealthStatus(c.status) != HealthStatus.OK for c in check_results)
            else HealthStatus.OK
        )

        # Update checks object with component checks
        self.checks = {
            f"{c.component_name}:{c.measurement_name}": c for c in check_results
        }

        # Update checks with system checks
        self.checks.update(self._system_checks())

        # Finish updating checks with recorded timestamp
        self.last_checked_timestamp = datetime.utcnow()

    def _system_checks(self) -> Dict[str, ComponentHealth]:
        """
        Returns system checks.
        """
        return {
            "uptime": ComponentHealth(
                component_type="system",
                measurement_name="uptime",
                status=HealthStatus.OK,
                observed_unit="s",
                observed_value=(
                    datetime.utcnow() - self.startup_timestamp
                ).total_seconds()
                if self.startup_timestamp
                else None,
                time=datetime.utcnow().isoformat(),
            )
        }

    def add_check_runner(self, runner: CheckRunner) -> None:
        """
        Add runner to run component health checks.

        Args:
            runner (CheckRunner): check runner instance.
        """
        if runner not in self.runners:
            self.runners.append(runner)
