from typing import Optional, Iterable, Tuple
from urllib.parse import urlsplit, urlunsplit
from playwright.sync_api import Page, expect
import pytest
import re


def navigate_home(page: Page, *, timeout: int = 10_000) -> None:
    """Deterministically land on /app/home regardless of current route.

    Why: SPA history/back can be flaky; we force-load home via absolute URL.
    """
    parts = urlsplit(page.url)
    origin = urlunsplit((parts.scheme, parts.netloc, "", "", ""))
    home_url = f"{origin}/app/home"
    page.goto(home_url)
    expect(page).to_have_url(re.compile(r"/app/home(?:$|/|\?.*)"), timeout=timeout)


def assert_link(
    page: Page,
    name: str,
    testid: str,
    href_pattern: str,
    *,
    click_and_check: bool = True,
    url_pattern: Optional[str] = None,
    timeout: int = 10_000,
) -> None:
    """Reusable assertion for sidebar links.

    `href_pattern` should be the *path only* (no query). Use `url_pattern` if the
    post-click URL includes query params (e.g., `?page=1`).
    """
    link = page.get_by_test_id(testid)
    expect(link).to_be_visible(timeout=timeout)
    expect(link).to_have_accessible_name(name)

    anchored = re.compile(rf"^\s*{re.escape(name)}\s*$", re.I)
    expect(link.locator("span")).to_have_text(anchored)

    role_link = page.get_by_role("link", name=anchored)
    expect(role_link).to_be_visible(timeout=timeout)
    expect(role_link).to_have_count(1)

    # Attribute is typically path-only; do not require query params here (no query).
    expect(role_link).to_have_attribute("href", re.compile(rf"^{href_pattern}$"))

    if click_and_check:
        # Allow query (e.g., `?page=1`) by default unless caller overrides.
        url_rx = re.compile(url_pattern or rf"{href_pattern}(?:$|/|\?.*)")

        role_link.click()
        expect(page).to_have_url(url_rx, timeout=timeout)

        # Always drive back to home explicitly to avoid SPA history quirks.
        navigate_home(page, timeout=timeout)


def sidebar_cases() -> Iterable[Tuple[str, str, str]]:
    """(name, testid, href_pattern) tuples for parametrized test."""
    return (
        ("Browse", "parent-browseLink", r"/app/browse"),
        ("Project Status", "parent-projectStatusLink", r"/app/project-status"),
        ("Dashboard", "parent-dashboardLink", r"/app/dashboard"),
        ("Stock Management", "parent-stockManagement", r"/app/sensor-management"),
        ("Admin", "parent-userManagementLink", r"/app/user-management"),
        ("Change logs", "parent-logsLink", r"/app/logs"),
    )


@pytest.fixture(scope="function")
def ensure_home(login: Page) -> Page:
    """Guarantee we're on /app/home before each test."""
    page: Page = login
    navigate_home(page)
    return page


def test_login_greeting(ensure_home: Page) -> None:
    """Basic smoke: post-login land on home and greeting visible."""
    page = ensure_home
    greeting = page.get_by_text("Hello,", exact=False)
    expect(greeting).to_be_visible()


@pytest.mark.parametrize(
    "name,testid,href_pattern",
    sidebar_cases(),
    ids=[n for n, *_ in sidebar_cases()],
)
def test_sidebar_link_navigates(ensure_home: Page, name: str, testid: str, href_pattern: str) -> None:
    page = ensure_home

    # Override expected post-click URLs where the app appends query params
    url_overrides = {
        "Stock Management": r"/app/sensor-management\?page=1(?:$|&)",
        "Change logs": r"/app/logs\?page=1(?:$|&)",
    }
    assert_link(
        page,
        name=name,
        testid=testid,
        href_pattern=href_pattern,
        url_pattern=url_overrides.get(name),
    )
