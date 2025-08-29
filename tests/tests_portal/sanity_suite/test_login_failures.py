import re
import pytest
from playwright.sync_api import expect

LOGIN_URL = "https://zealous-ground-067dafc03.4.azurestaticapps.net/auth/login"

@pytest.mark.parametrize(
    "email,password,expected_pattern",
    [
        ("xxy@gmail.com", "WrongPassword123!", r"incorrect email or password"),
        ("xxy@gmail.com", "",                   r"required"),
        ("",               "WrongPassword123!", r"required"),
    ],
    ids=["invalid-credentials", "missing-password", "missing-email"],
)
def test_login_negative_cases(page, email, password, expected_pattern):
    page.goto(LOGIN_URL, wait_until="domcontentloaded")

    # Fill (or clear) fields
    page.get_by_label(re.compile(r"email", re.I)).fill(email)
    page.get_by_label(re.compile(r"password", re.I)).fill(password)

    # Submit
    page.get_by_role("button", name=re.compile(r"^sign in$", re.I)).click()
    page.wait_for_load_state("networkidle")  # give the UI a moment

    # We should stay on the login page
    expect(page).to_have_url(re.compile(r"/auth/login"))

    # Assert the error — prefer ARIA alert, fall back to visible text
    pattern = re.compile(expected_pattern, re.I)
    try:
        expect(page.get_by_role("alert")).to_contain_text(pattern)
    except Exception:
        expect(page.get_by_text(pattern).first).to_be_visible(timeout=8000)
