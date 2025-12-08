"""
E2E-specific pytest configuration.
This allows running E2E tests against either:
1. The fastapi_server fixture (auto-started test server)
2. An external server URL via --base-url option
"""
import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--base-url",
        action="store",
        default=None,
        help="Base URL of the running server for E2E tests (e.g., http://localhost:8080)"
    )

@pytest.fixture(scope="session")
def base_url(request):
    """
    Return the base URL for E2E tests.
    If --base-url is provided, use that (external server).
    Otherwise, try to use the fastapi_server fixture (auto-started).
    """
    external_url = request.config.getoption("--base-url")
    if external_url:
        # Use external server
        return external_url.rstrip('/') + '/'
    else:
        # Try to use auto-started test server
        try:
            from ..conftest import fastapi_server
            return request.getfixturevalue('fastapi_server')
        except Exception as e:
            pytest.skip(f"No base URL provided and fastapi_server fixture failed: {e}")
