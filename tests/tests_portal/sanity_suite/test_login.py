from playwright.sync_api import Page, expect
import re


def assert_link(page: Page, name: str, testid: str, href_pattern: str) -> None:
    """Reusable assertion for sidebar links."""
    link = page.get_by_test_id(testid)
    expect(link).to_be_visible()
    expect(link).to_have_accessible_name(name)
    expect(link.locator("span")).to_have_text(re.compile(rf"^\s*{re.escape(name)}\s*$", re.I))

    role_link = page.get_by_role("link", name=re.compile(rf"^\s*{re.escape(name)}\s*$", re.I))
    expect(role_link).to_be_visible()
    expect(role_link).to_have_count(1)

    # Check href attribute matches expected pattern
    expect(role_link).to_have_attribute("href", re.compile(href_pattern))


def test_login_success(login: Page) -> None:
    page: Page = login

    # Wait for app shell to be ready (route after auth). Avoid content scraping.
    expect(page).to_have_url(re.compile(r"/app/home$"))

    # Assert sidebar "Browse" link
    assert_link(page, name="Browse", testid="parent-browseLink", href_pattern=r"/app/browse")

    # Assert greeting appears somewhere on the page
    greeting = page.get_by_text("Hello,", exact=False)
    expect(greeting).to_be_visible()

    # Optional: sanity-check SVG icon exists
    expect(page.locator("[data-testid='parent-browseLink'] svg")).to_have_count(1)

def test_navigate_tabs(login):
    login.click("text=Browse")
    assert "Select a data type to begin browsing." in login.content()