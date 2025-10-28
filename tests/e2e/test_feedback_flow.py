"""E2E tests for feedback submission flow."""
import pytest
from playwright.sync_api import Page, expect
from tests.e2e.utils import (
    wait_for_reflex_hydration,
    reflex_click,
    reflex_fill,
    debug_page_content
)


@pytest.mark.e2e
class TestFeedbackSubmission:
    """Test feedback submission user flow."""

    def test_feedback_page_loads(self, page: Page, base_url):
        """Test that feedback page loads with parameters."""
        # Navigate with query parameters
        page.goto(f"{base_url}/?order_id=TEST001&courier_id=123")

        # Wait for Reflex to hydrate
        wait_for_reflex_hydration(page)

        # Debug: Print page content if test fails
        # debug_page_content(page)

        # Check for main heading - use flexible selectors
        heading = page.locator("text=Rate Your Delivery").or_(
            page.locator("h1")
        ).first
        expect(heading).to_be_visible(timeout=10000)

        # Check order ID is displayed
        expect(page.locator("text=/Order ID.*TEST001/i")).to_be_visible()

    def test_submit_5_star_feedback(self, page: Page, base_url):
        """Test submitting positive feedback."""
        page.goto(f"{base_url}/?order_id=E2E_TEST_001&courier_id=123")
        wait_for_reflex_hydration(page)

        # Select 5 stars - Reflex renders buttons, find by icon or structure
        # Try multiple selector strategies
        stars = page.locator('button:has(svg)').filter(has_text="")
        if stars.count() > 0:
            stars.nth(4).click()  # 5th star (0-indexed)
        else:
            # Fallback: click any star-like element
            page.locator('[class*="star"]').nth(4).click()

        page.wait_for_timeout(500)  # Wait for state update

        # Fill comment
        comment_field = page.locator('textarea, input[type="text"]').first
        reflex_fill(page, 'textarea', "Excellent service!")

        # Check reason
        punctuality = page.locator('label:has-text("Punctuality")').or_(
            page.locator('text=Punctuality')
        ).first
        reflex_click(page, 'label:has-text("Punctuality")')

        # Consent checkbox
        consent = page.locator('text=agree to my feedback').or_(
            page.locator('input[type="checkbox"]')
        ).last
        consent.check()

        # Submit
        submit_btn = page.locator('button:has-text("Submit")')
        submit_btn.click()

        # Wait for success message
        page.wait_for_timeout(2000)

        # Check for thank you message
        thank_you = page.locator('text=/thank you/i').or_(
            page.locator('text=/submitted/i')
        )
        expect(thank_you).to_be_visible(timeout=10000)

    def test_form_validation(self, page: Page, base_url):
        """Test that submit is disabled without rating."""
        page.goto(f"{base_url}/?order_id=E2E_TEST_002&courier_id=123")
        wait_for_reflex_hydration(page)

        # Submit button should be disabled initially
        submit_btn = page.locator('button:has-text("Submit")')
        expect(submit_btn).to_be_disabled()


@pytest.mark.e2e
class TestAdminDashboard:
    """Test admin dashboard flow."""

    def test_admin_login_flow(self, page: Page, base_url):
        """Test admin can log in."""
        page.goto(f"{base_url}/admin")
        wait_for_reflex_hydration(page)

        # Fill login form
        reflex_fill(page, 'input[name="username"]', "admin")
        reflex_fill(page, 'input[type="password"]', "admin")

        # Submit
        page.locator('button:has-text("Login")').click()

        # Should redirect to dashboard
        page.wait_for_url("**/admin/dashboard", timeout=10000)

        # Check for dashboard elements
        expect(page.locator('text=/dashboard/i')).to_be_visible()
