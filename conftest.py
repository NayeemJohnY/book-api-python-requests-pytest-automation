"""Global Fixtures"""
import pytest
from helpers.api_client import APIClient


BASE_URI = "http://localhost:3000"
BASE_PATH = "/api/books"


@pytest.fixture(scope="module")
def api_client():
    """API Client Global Fixture"""
    return APIClient(BASE_URI,  BASE_PATH)


def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run is complete, after all parallel workers.
    Runs in the master process.
    """
    if hasattr(session.config, 'workerinput'):
        # This is a worker node (used by xdist), skip cleanup
        return

    client = APIClient(BASE_URI, BASE_PATH)
    res = client.delete(client.build_url("/reset"),
                        headers={"authorization": "Bearer admin-token"})


    assert res.status_code == 204, f"Reset failed: {res.status_code} {res.text}" # nosec
