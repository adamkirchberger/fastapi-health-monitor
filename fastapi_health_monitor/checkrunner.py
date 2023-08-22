import logging
from typing import Callable
from datetime import datetime

from .models import ComponentHealth
from .constants import HealthStatus


logger = logging.getLogger(__name__)


class CheckRunner:
    def __init__(
        self,
        component: ComponentHealth,
        check_function: Callable[[ComponentHealth], ComponentHealth],
    ) -> None:
        """
        A CheckRunner executes checks to determine the health status of a component.

        Args:
            component (ComponentHealth): component instance.
            check_function (Callable): Check function.
        """
        self.component: ComponentHealth = component
        self.check_function: Callable[
            [ComponentHealth], ComponentHealth
        ] = check_function

    async def run_check(self) -> ComponentHealth:
        """
        Run component check function and return response.

        Returns:
            ComponentHealth: component health response.
        """
        component = self.component
        # Run check
        try:
            # Update component by passing component to check function
            component = self.check_function(component)

        # Component check failed
        except Exception as e:  # pylint: disable=W0718
            logger.exception(e)
            component.status = HealthStatus.ERROR
            component.output = "Failed to run component health check function."

        # Update recorded time
        component.time = datetime.utcnow().isoformat()

        return component
