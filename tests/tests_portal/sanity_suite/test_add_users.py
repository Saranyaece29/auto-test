import re
import time
from playwright.sync_api import expect
from tests.tests_portal.helpers.user_management_ui import (
    select_random_role,
    select_random_currency,
    select_random_country_code,
    select_random_metric_system,
    select_random_unit,
    maybe_select_random_partner_if_visible,
    maybe_select_random_company_if_visible,
)

def test_create_new_user(login, urls, request):
    page = login
    page.click("text=Admin")
    page.click("text=Add User")

    # Unique identity
    suffix = str(int(time.time()))[-6:]
    first_name = f"Test_auto_{suffix}"
    last_name = "User"
    email = f"test.autouser.{suffix}@example.com"
    phone = f"07123{suffix}"

    # Fill fields
    page.get_by_test_id("first-name").fill(first_name)
    page.get_by_test_id("last-name").fill(last_name)
    page.get_by_test_id("email").fill(email)
    page.get_by_test_id("input-phone").fill(phone)

    # Role may enable Partner/Company -->Conditionally select Partner / Company if those dropdowns appear for this role
    role = select_random_role(page)
    maybe_select_random_partner_if_visible(page)
    maybe_select_random_company_if_visible(page)

    select_random_currency(page)
    select_random_country_code(page)
    select_random_metric_system(page)
    select_random_unit(page, "FlowRateUnit")
    select_random_unit(page, "LongDistanceUnit")
    select_random_unit(page, "VolumeUnit")
    select_random_unit(page, "ShortDistanceUnit")
    select_random_unit(page, "WeightUnit")
    select_random_unit(page, "DiameterUnit")

    # Submit
    submit_btn = page.get_by_role("button", name=re.compile(r"^Add New User$", re.I))
    expect(submit_btn).to_be_enabled(timeout=10000)
    submit_btn.click()

    #validate success message
    try:
        expect(page.get_by_text(re.compile(r"The user has been successfully created", re.I))).to_be_visible(timeout=10000)
    except Exception:
        pass

    # Validate newly created user in the view users list
    try:
        page.click("text=View Users")
    except Exception:
        if isinstance(urls, dict) and "VIEW_USERS_URL" in urls:
            page.goto(urls["VIEW_USERS_URL"], wait_until="domcontentloaded")

    search = page.get_by_placeholder(re.compile(r"^Search$", re.I))
    search.fill(email)

    rows = page.get_by_test_id("table-row")
    target_row = rows.filter(has_text=email).first
    expect(target_row).to_be_visible(timeout=15000)
    expect(target_row).to_contain_text(first_name)
