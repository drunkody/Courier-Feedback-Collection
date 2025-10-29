"""Pytest fixtures for Playwright E2E tests."""
import pytest
from playwright.sync_api import sync_playwright, Browser, Page, BrowserContext
from ..playwright_config import ReflexTestServer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def reflex_server():
    """Start Reflex server for all E2E tests."""
    server = ReflexTestServer(mode="hybrid", port=3000)

    try:
        server.start(timeout=90)
        yield server
    finally:
        server.stop()


@pytest.fixture(scope="session")
def browser():
    """Launch browser for tests."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,  # Set to False for debugging
            args=['--disable-dev-shm-usage']  # Helps in CI
        )
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser):
    """Create browser context for each test."""
    context = browser.new_context(
        viewport={"width": 1280, "height": 720},
        locale="en-US",
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext, reflex_server):
    """Create page for each test."""
    page = context.new_page()

    # Setup console logging for debugging
    page.on("console", lambda msg: logger.debug(f"Console: {msg.text}"))
    page.on("pageerror", lambda err: logger.error(f"Page error: {err}"))

    yield page
    page.close()


@pytest.fixture(scope="session")
def base_url(reflex_server):
    """Get base URL for tests."""
    return f"http://localhost:{reflex_server.port}"
