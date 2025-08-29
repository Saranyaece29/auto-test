import os
import re
import pytest
from urllib.parse import urlsplit, urlunsplit
from playwright.sync_api import Page, expect


BASE_URL = os.getenv(
    "PORTAL_BASE_URL",
    "https://zealous-ground-067dafc03.4.azurestaticapps.net",
)
LOGIN_URL = f"{BASE_URL}/auth/login"
FORGOT_URL = f"{BASE_URL}/auth/forgot"


# --- helpers ---------------------------------------------------------------

def _origin(page: Page) -> str:
    parts = urlsplit(page.url)
    return urlunsplit((parts.scheme, parts.netloc, "", "", ""))


def navigate_login(page: Page, *, timeout: int = 10_000) -> None:
    page.goto(LOGIN_URL, wait_until="domcontentloaded")
    expect(page).to_have_url(re.compile(r"/auth/login"), timeout=timeout)


def navigate_forgot(page: Page, *, timeout: int = 10_000) -> None:
    page.goto(FORGOT_URL, wait_until="domcontentloaded")
    expect(page).to_have_url(re.compile(r"/auth/forgot"), timeout=timeout)


# --- tests: Login page UI --------------------------------------------------

def test_login_page_ui_elements(page: Page) -> None:
    """Validate Login page static UI."""
    navigate_login(page)

    # Form container
    form = page.get_by_test_id("login-form")
    expect(form).to_be_visible()

    # Headings / text
    expect(page.get_by_role("heading", name="Sign In to Admin Panel")).to_be_visible()
    expect(page.get_by_text("Enter your email and password below")).to_be_visible()

    # Inputs
    email = page.get_by_test_id("login-email")
    expect(email).to_be_visible()
    expect(email).to_have_attribute("type", "email")
    expect(email).to_have_attribute("placeholder", re.compile(r"enter your email", re.I))

    password = page.get_by_test_id("login-password")
    expect(password).to_be_visible()
    expect(password).to_have_attribute("type", "password")
    expect(password).to_have_attribute("placeholder", re.compile(r"enter your password", re.I))

    # Buttons
    sign_in_btn = page.get_by_role("button", name=re.compile(r"^Sign In$", re.I))
    expect(sign_in_btn).to_be_visible()
    expect(sign_in_btn).to_be_enabled()

    okta_btn = page.get_by_role("button", name=re.compile(r"^Login with Okta$", re.I))
    expect(okta_btn).to_be_visible()
    expect(okta_btn).to_be_enabled()

    # Forgot link
    forgot_link = page.get_by_role("link", name=re.compile(r"^Forgot Password\?$", re.I))
    expect(forgot_link).to_be_visible()
    expect(forgot_link).to_have_attribute("href", re.compile(r"/auth/forgot$"))

    # Smoke: still on login
    expect(page).to_have_url(re.compile(r"/auth/login"))


# --- tests: Forgot Password flow ------------------------------------------

def test_forgot_password_link_ui(page: Page) -> None:
    """Validate forgot link → page UI."""
    navigate_login(page)

    forgot = page.get_by_role("link", name="Forgot Password?")
    expect(forgot).to_be_visible()
    expect(forgot).to_have_attribute("href", re.compile(r"/auth/forgot$"))

    forgot.click()
    expect(page).to_have_url(re.compile(r"/auth/forgot"))

    # Forgot page UI
    expect(page.get_by_role("heading", name="Forgot Password")).to_be_visible()
    expect(page.get_by_text(re.compile(r"^Enter your email below$", re.I))).to_be_visible()

    email = page.get_by_test_id("email")
    expect(email).to_be_visible()
    expect(email).to_have_attribute("type", "email")
    expect(email).to_have_attribute("placeholder", re.compile(r"enter your email", re.I))

    submit_btn = page.get_by_test_id("submit").get_by_role("button", name="Send reset link")
    expect(submit_btn).to_be_visible()
    expect(submit_btn).to_be_enabled()


@pytest.mark.parametrize("email_addr", [
    "sup_adm_user@fido.tech",
])
def test_forgot_password_submit_shows_confirmation(page: Page, email_addr: str) -> None:
    """Submit the email and confirm success via toast or redirect to login."""
    navigate_forgot(page)

    page.get_by_test_id("email").fill(email_addr)
    page.get_by_test_id("submit").get_by_role("button", name="Send reset link").click()

    #Toast confirmation visible
    toast_container = page.locator(".Toastify")
    #phrases = ["sent", "successfully", "recovery link", "email"]
    phrases = ["Recovery link was sent successfully to your email"]    
    for p in phrases:
        try:
            expect(toast_container.get_by_text(re.compile(p, re.I))).to_be_visible(timeout=5000)
            return
        except AssertionError:
            pass

    # Redirect back to login
    try:
        expect(page).to_have_url(re.compile(r"/auth/login"), timeout=8000)
        expect(page.get_by_test_id("loginPage")).to_be_visible()
        expect(page.get_by_role("heading", name=re.compile(r"Sign In to Admin Panel", re.I))).to_be_visible()
        return
    except AssertionError:
        pass

    raise AssertionError(f"No success toast and no redirect to login. Current URL: {page.url}")
