from playwright.sync_api import Page, expect
import time

def test_tire_wear_display(page: Page):
    """
    This test verifies that the tire wear information is displayed correctly.
    """
    # 1. Arrange: Go to the running Streamlit app.
    page.goto("http://localhost:8501")

    # Add a small delay to allow the page to load
    time.sleep(5)

    # 2. Assert: Check that the tire status elements are visible.
    expect(page.get_by_text("FL")).to_be_visible()
    expect(page.get_by_text("FR")).to_be_visible()
    expect(page.get_by_text("RL")).to_be_visible()
    expect(page.get_by_text("RR")).to_be_visible()

    # 3. Assert: Check that the "Wear" text is visible for each tire.
    expect(page.get_by_text("Wear:", exact=False)).to_have_count(4)

    # 4. Screenshot: Capture the final result for visual verification.
    page.screenshot(path="jules-scratch/verification/verification.png")