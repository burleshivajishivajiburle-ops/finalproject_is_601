import os
import socket
import subprocess
import sys
import time
import logging
from pathlib import Path
from typing import Generator, Dict, List
from contextlib import contextmanager

import pytest
import requests

try:
    from faker import Faker  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback when Faker isn't installed
    import random
    from uuid import uuid4

    class _FallbackUnique:
        def __init__(self, parent: "_FallbackFaker") -> None:
            self._parent = parent

        def email(self) -> str:
            return self._parent._unique_email()

        def user_name(self) -> str:
            return self._parent._unique_username()

    class _FallbackFaker:
        def __init__(self) -> None:
            self.unique = _FallbackUnique(self)

        @staticmethod
        def seed(_: int) -> None:
            random.seed(12345)

        def first_name(self) -> str:
            return f"First{random.randint(1, 9999)}"

        def last_name(self) -> str:
            return f"Last{random.randint(1, 9999)}"

        def _unique_email(self) -> str:
            suffix = uuid4().hex[:8]
            return f"user{suffix}@example.com"

        def _unique_username(self) -> str:
            return f"user_{uuid4().hex[:10]}"

        def password(self, length: int = 12) -> str:
            base = "P@ssw0rd"
            while len(base) < length:
                base += random.choice("abcdef123456")
            return base[:length]

    def Faker() -> _FallbackFaker:  # type: ignore
        return _FallbackFaker()

    Faker.seed = staticmethod(lambda _: None)  # type: ignore[attr-defined]
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, get_engine, get_sessionmaker
from app.models.user import User
from app.core.config import settings
from app.database_init import init_db, drop_db

# ======================================================================================
# Logging Configuration
# ======================================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ======================================================================================
# Database Configuration
# ======================================================================================
fake = Faker()
Faker.seed(12345)

# Configure test engine with SQLite-specific options to handle concurrent access
from sqlalchemy import create_engine, event
test_engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,
        "isolation_level": None  # Autocommit mode
    },
    poolclass=None,  # Disable pooling for tests to avoid connection issues
    echo=False
)

# Enable WAL mode for better concurrency
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=30000")  # 30 second timeout
    cursor.close()

TestingSessionLocal = get_sessionmaker(engine=test_engine)

# ======================================================================================
# Helper Functions
# ======================================================================================
def create_fake_user() -> Dict[str, str]:
    """Generate a dictionary of fake user data for testing."""
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.unique.email(),
        "username": fake.unique.user_name(),
        "password": fake.password(length=12)
    }

@contextmanager
def managed_db_session():
    """Context manager for safe database session handling."""
    session = TestingSessionLocal()
    try:
        yield session
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()

# ======================================================================================
# Server Startup / Healthcheck
# ======================================================================================
def wait_for_server(url: str, timeout: int = 30) -> bool:
    """
    Wait for the server to be ready by repeatedly issuing GET requests until
    we receive a 200 status code or hit the timeout.
    """
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    return False

class ServerStartupError(Exception):
    """Raised when the test server fails to start properly."""
    pass

# ======================================================================================
# Database Fixtures
# ======================================================================================
@pytest.fixture(scope="session")
def setup_test_database(request):
    """
    Set up the test database before the session starts, and tear it down after tests
    unless --preserve-db is provided.
    NOTE: This fixture is NOT autouse - it must be explicitly requested by tests
    to avoid conflicts with the E2E server fixture.
    """
    logger.info("Setting up test database...")
    try:
        # Only create tables if they don't exist (avoid dropping to prevent locks)
        Base.metadata.create_all(bind=test_engine, checkfirst=True)
        init_db()
        logger.info("Test database initialized.")
    except Exception as e:
        logger.error(f"Error setting up test database: {str(e)}")
        raise

    yield  # Tests run after this

    if not request.config.getoption("--preserve-db"):
        logger.info("Dropping test database tables...")
        drop_db()

@pytest.fixture
def db_session(setup_test_database) -> Generator[Session, None, None]:
    """
    Provide a test-scoped database session. Commits after a successful test;
    rolls back if an exception occurs.
    NOTE: Explicitly depends on setup_test_database to ensure DB is initialized.
    """
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# ======================================================================================
# Test Data Fixtures
# ======================================================================================
@pytest.fixture
def fake_user_data() -> Dict[str, str]:
    """Provide fake user data."""
    return create_fake_user()

@pytest.fixture
def test_user(db_session: Session) -> User:
    """
    Create and return a single test user in the database with hashed password.
    The password is set to 'TestPass123' for consistent testing.
    """
    user_data = create_fake_user()
    # Use a consistent password for testing
    user_data.pop("password")  # Remove random password
    from app.models.user import User as UserModel
    hashed_password = UserModel.hash_password("TestPass123")
    user = User(**user_data, password=hashed_password)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    logger.info(f"Created test user ID: {user.id}")
    return user

@pytest.fixture
def seed_users(db_session: Session, request) -> List[User]:
    """
    Seed multiple test users in the database. By default, 5 users are created
    unless a 'param' value is provided (e.g., via @pytest.mark.parametrize).
    """
    num_users = getattr(request, "param", 5)
    users = [User(**create_fake_user()) for _ in range(num_users)]
    db_session.add_all(users)
    db_session.commit()
    logger.info(f"Seeded {len(users)} users.")
    return users

# ======================================================================================
# FastAPI Server Fixture
# ======================================================================================
def find_available_port() -> int:
    """Find an available port for the test server by binding to port 0."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

@pytest.fixture(scope="session")
def fastapi_server():
    """
    Start a FastAPI test server in a subprocess. If the chosen port (default: 8000)
    is already in use, find another available port. Wait until the server is up
    before yielding its base URL.
    """
    base_port = 5555  # Use different port to avoid conflicts
    server_url = f'http://127.0.0.1:{base_port}/'

    # Check if port is free; if not, pick an available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(('127.0.0.1', base_port)) == 0:
            base_port = find_available_port()
            server_url = f'http://127.0.0.1:{base_port}/'

    logger.info(f"Starting FastAPI server on port {base_port}...")

    project_root = Path(__file__).resolve().parents[1]
    
    # Use environment variable to set a different database for E2E tests
    env = os.environ.copy()
    env['DATABASE_URL'] = 'sqlite:///test_e2e.db'
    
    # Clean up old database file before starting
    test_db_path = project_root / "test_e2e.db"
    for ext in ['', '-shm', '-wal']:
        db_file = Path(str(test_db_path) + ext)
        if db_file.exists():
            try:
                db_file.unlink()
                logger.info(f"Cleaned up {db_file}")
            except Exception as e:
                logger.warning(f"Could not delete {db_file}: {e}")
    
    uvicorn_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(base_port),
    ]

    # Use DEVNULL for both stdout and stderr to avoid blocking
    process = subprocess.Popen(
        uvicorn_cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=str(project_root),
        env=env
    )

    # IMPORTANT: Use the /health endpoint for the check!
    health_url = f"{server_url}health"
    if not wait_for_server(health_url, timeout=30):
        logger.error(f"Server failed to start on {health_url}")
        process.terminate()
        process.wait(timeout=5)
        raise ServerStartupError(f"Failed to start test server on {health_url}. Check if port {base_port} is available.")

    logger.info(f"Test server running on {server_url}.")
    yield server_url

    logger.info("Stopping test server...")
    process.terminate()
    try:
        process.wait(timeout=5)
        logger.info("Test server stopped.")
    except subprocess.TimeoutExpired:
        process.kill()
        logger.warning("Test server forcefully stopped.")
    
    # Clean up test database after tests
    test_db_path = project_root / "test_e2e.db"
    for ext in ['', '-shm', '-wal']:
        db_file = Path(str(test_db_path) + ext)
        if db_file.exists():
            try:
                db_file.unlink()
            except Exception:
                pass

# ======================================================================================
# Playwright Fixtures for UI Testing
# ======================================================================================
@pytest.fixture(scope="session")
def browser_context():
    """Provide a Playwright browser context for UI tests (session-scoped)."""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        logger.info("Playwright browser launched.")
        try:
            yield browser
        finally:
            logger.info("Closing Playwright browser.")
            browser.close()

@pytest.fixture
def page(browser_context):
    """
    Provide a new browser page for each test, with a standard viewport.
    Closes the page and context after each test.
    """
    context = browser_context.new_context(
        viewport={'width': 1920, 'height': 1080},
        ignore_https_errors=True
    )
    page = context.new_page()
    logger.info("New browser page created.")
    try:
        yield page
    finally:
        logger.info("Closing browser page and context.")
        page.close()
        context.close()

@pytest.fixture(scope="session")
def base_url(fastapi_server):
    """
    Provide the base URL for E2E tests.
    Depends on fastapi_server fixture to ensure server is running.
    """
    return fastapi_server

@pytest.fixture
def test_user_credentials(base_url):
    """
    Create a test user via API and return credentials for E2E tests.
    This fixture registers a user through the running E2E server.
    If user already exists (e.g., testing against external server), try to use them.
    """
    import requests
    from faker import Faker
    import time
    fake = Faker()
    
    # Use a timestamp-based username to avoid collisions
    timestamp = int(time.time())
    username = f"testuser{timestamp}"
    email = f"test{timestamp}@example.com"
    password = "TestPass123!"
    
    # Ensure base_url ends with /
    url = base_url if base_url.endswith('/') else f"{base_url}/"
    
    # Register user through API
    response = requests.post(
        f"{url}auth/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": email,
            "username": username,
            "password": password,
            "confirm_password": password
        }
    )
    
    if response.status_code not in [200, 201]:
        # If user exists, that's okay for external servers
        if "already exists" in response.text.lower():
            logger.warning(f"User {username} already exists, trying different username")
            # Try with a more unique identifier
            username = f"testuser{timestamp}_{fake.random_int(1000, 9999)}"
            email = f"test{timestamp}_{fake.random_int(1000, 9999)}@example.com"
            response = requests.post(
                f"{url}auth/register",
                json={
                    "first_name": "Test",
                    "last_name": "User",
                    "email": email,
                    "username": username,
                    "password": password,
                    "confirm_password": password
                }
            )
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create test user: {response.status_code} - {response.text}")
        else:
            raise Exception(f"Failed to create test user: {response.status_code} - {response.text}")
    
    return {
        "username": username,
        "email": email,
        "password": password,
        "first_name": "Test",
        "last_name": "User"
    }

# ======================================================================================
# Pytest Command-Line Options
# ======================================================================================
def pytest_addoption(parser):
    """
    Add custom command line options:
      --preserve-db : Keep test database after tests
      --run-slow    : Run tests marked as 'slow'
    """
    parser.addoption("--preserve-db", action="store_true", help="Keep test database after tests")
    parser.addoption("--run-slow", action="store_true", help="Run tests marked as slow")

def pytest_collection_modifyitems(config, items):
    """
    Skip tests marked as 'slow' unless --run-slow is specified.
    """
    if not config.getoption("--run-slow"):
        skip_slow = pytest.mark.skip(reason="use --run-slow to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
