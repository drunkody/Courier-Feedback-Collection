import sys
sys.path.append('.')

from playwright.sync_api import sync_playwright
from tests.playwright_config import ReflexTestServer
from tests.e2e.utils import wait_for_reflex_hydration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run(playwright):
    server = ReflexTestServer(mode="hybrid", port=3000)
    try:
        server.start(timeout=90)

        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("http://localhost:3000/?order_id=TEST001&courier_id=123")
        wait_for_reflex_hydration(page)
        page.screenshot(path="jules-scratch/verification/feedback_page.png")

        page.goto("http://localhost:3000/admin")
        wait_for_reflex_hydration(page)
        page.screenshot(path="jules-scratch/verification/admin_login_page.png")

        page.locator("input[name=username]").fill("admin")
        page.locator("input[name=password]").fill("admin")
        page.screenshot(path="jules-scratch/verification/admin_login_page_filled.png")
        page.get_by_role("button", name="Login").click()
        page.wait_for_timeout(5000)
        page.screenshot(path="jules-scratch/verification/admin_login_page_after_click.png")
        page.wait_for_url("http://localhost:3000/admin/dashboard")
        wait_for_reflex_hydration(page)
        page.screenshot(path="jules-scratch/verification/admin_dashboard_page.png")

        context.close()
        browser.close()
    finally:
        server.stop()

with sync_playwright() as playwright:
    run(playwright)
