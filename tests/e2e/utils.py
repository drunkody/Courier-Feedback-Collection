"""Utilities for Playwright tests with Reflex."""
from playwright.sync_api import Page, expect
import time

def wait_for_reflex_hydration(page: Page, timeout=10000):
    """
    Wait for Reflex to fully hydrate.
    Reflex uses WebSocket and needs time to initialize state.
    """
    # Wait for the main app container
    page.wait_for_selector("body", timeout=timeout)

    # Wait for no more network activity (sign of hydration complete)
    page.wait_for_load_state("networkidle", timeout=timeout)

    # Additional wait for WebSocket connection
    time.sleep(1)

    # Check if there are any loading spinners
    try:
        loading = page.locator('[class*="loading"]')
        loading.wait_for(state="detached", timeout=5000)
    except:
        pass


def reflex_click(page: Page, selector: str, timeout=5000):
    """
    Click element with Reflex-specific wait.
    Handles Reflex's event system delays.
    """
    element = page.locator(selector)
    element.wait_for(state="visible", timeout=timeout)
    element.scroll_into_view_if_needed()
    element.click()
    time.sleep(0.3)  # Wait for Reflex state update


def reflex_fill(page: Page, selector: str, value: str, timeout=10000):
    """Fill input with Reflex-specific handling."""
    element = page.locator(selector)
    element.wait_for(state="visible", timeout=timeout)
    element.click()  # Focus
    element.fill(value)
    element.blur()  # Trigger onChange
    time.sleep(0.2)  # Wait for Reflex state update


def debug_page_content(page: Page):
    """Print page content for debugging."""
    print("\n=== PAGE CONTENT ===")
    print(f"URL: {page.url}")
    print(f"Title: {page.title()}")
    print("\n=== HTML ===")
    print(page.content())
    print("\n=== CONSOLE ERRORS ===")
    # This needs to be set up in the test with page.on("console")


def get_reflex_state(page: Page, state_name: str):
    """Get Reflex state value from client."""
    return page.evaluate(f"""
        () => {{
            // Access Reflex's internal state if exposed
            return window.__reflex_state ? window.__reflex_state['{state_name}'] : null;
        }}
    """)
