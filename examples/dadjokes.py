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
