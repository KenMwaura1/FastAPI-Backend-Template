import fastapi
import httpx
import pytest
import pytest_asyncio
import typing

from src.main import initialize_backend_application


@pytest.fixture(name="backend_test_app")
def backend_test_app() -> fastapi.FastAPI:
    """
    A fixture that re-initializes the FastAPI instance for test application.
    """

    return initialize_backend_application()


@pytest_asyncio.fixture(name="initialize_backend_test_application")
async def initialize_backend_test_application(backend_test_app: fastapi.FastAPI) -> typing.AsyncGenerator[fastapi.FastAPI, None]:
    await backend_test_app.router.startup()
    yield backend_test_app
    await backend_test_app.router.shutdown()


@pytest_asyncio.fixture(name="async_client")
async def async_client(initialize_backend_test_application: fastapi.FastAPI) -> typing.AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=initialize_backend_test_application),
            base_url="http://testserver",
            headers={"Content-Type": "application/json"},
        ) as client:
        yield client
