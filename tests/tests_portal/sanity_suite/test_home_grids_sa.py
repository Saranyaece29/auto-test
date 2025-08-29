from urllib.parse import urlsplit, urlunsplit
from playwright.sync_api import Page, expect
import pytest
import re


# --- helpers ---------------------------------------------------------------

def navigate_home(page: Page, *, timeout: int = 10_000) -> None:
    parts = urlsplit(page.url)
    origin = urlunsplit((parts.scheme, parts.netloc, "", "", ""))
    home_url = f"{origin}/app/home"
    page.goto(home_url)
    expect(page).to_have_url(re.compile(r"/app/home(?:$|/|\?.*)"), timeout=timeout)


def assert_home_card(
    page: Page,
    name: str,
    href: str,
    *,
    timeout: int = 10_000,
) -> None:
    """Assert a home grid card by its heading text; then click and verify URL.

    We locate the heading first to avoid colliding with sidebar links that share hrefs.
    """
    heading_rx = re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)
    heading = page.locator("div.text-h5").filter(has_text=heading_rx).first
    expect(heading).to_be_visible(timeout=timeout)

    card = heading.locator("xpath=ancestor::a[1]")
    expect(card).to_be_visible(timeout=timeout)

    expect(card).to_have_attribute("href", re.compile(rf"^{re.escape(href)}$"))

    card.click()
    expect(page).to_have_url(re.compile(rf"{re.escape(href)}(?:$|/|\?.*)"), timeout=timeout)

    # Reset to home for the next case
    navigate_home(page, timeout=timeout)


def home_card_cases():
    return (
        ("Locate leaks", "/app/browse/waypoints"),
        ("Monitor your network", "/app/browse/relays"),
        ("Manage projects", "/app/project-status"),
        ("Your dashboards", "/app/dashboard"),
    )


# --- fixtures --------------------------------------------------------------

@pytest.fixture(scope="function")
def ensure_home(login: Page) -> Page:
    page: Page = login
    navigate_home(page)
    return page


# --- tests -----------------------------------------------------------------

@pytest.mark.parametrize(
    "name,href",
    home_card_cases(),
    ids=[n for n, _ in home_card_cases()],
)
def test_home_cards_navigate(ensure_home: Page, name: str, href: str) -> None:
    page = ensure_home
    assert_home_card(page, name=name, href=href)
