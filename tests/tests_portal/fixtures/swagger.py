import os
import re
import pytest
from playwright.sync_api import sync_playwright, expect, Page

# ---- App config (pull secrets from env; fall back to placeholders) ----
LOGIN_URL = "https://zealous-ground-067dafc03.4.azurestaticapps.net/auth/login"
BASE = "https://zealous-ground-067dafc03.4.azurestaticapps.net/app"
ADD_PARTNER_URL = f"{BASE}/user-management/add-partner"
VIEW_PARTNERS_URL = f"{BASE}/user-management/view-partners"
ADD_COMPANY_URL = f"{BASE}/user-management/add-company"
VIEW_COMPANIES_URL = f"{BASE}/user-management/view-companies"

EMAIL = os.getenv("APP_EMAIL", "sup_adm_user@fido.tech")
PASSWORD = os.getenv("APP_PASSWORD", "GAN@$P!59Lm3BgyUAiVm")

@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p

@pytest.fixture(scope="session")
def browser(playwright_instance):
    # Toggle headless/slowmo via env if you like
    headless = os.getenv("HEADLESS", "false").lower() == "true"
    slow_mo = int(os.getenv("SLOW_MO", "0"))
    browser = playwright_instance.chromium.launch(headless=headless, slow_mo=slow_mo)
    yield browser
    browser.close()

@pytest.fixture
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()

@pytest.fixture
def login(page: Page):
    """Log in and return an authenticated page."""
    page.goto(LOGIN_URL)
    page.fill("input[name='email']", EMAIL)
    page.fill("input[name='password']", PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_url("**/app/**", timeout=15000)
    return page

@pytest.fixture
def urls():
    """Expose common URLs so tests can import nothing."""
    return {
        "ADD_PARTNER_URL": ADD_PARTNER_URL,
        "VIEW_PARTNERS_URL": VIEW_PARTNERS_URL,
    }
