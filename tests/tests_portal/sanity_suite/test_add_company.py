import re
import time
from playwright.sync_api import expect
from tests.tests_portal.helpers.user_management_ui import (
    select_random_country,
    select_random_measurement,
    select_random_partner,
    select_random_currency
)


def test_create_new_company(login, urls, request):
    page = login
    #page.goto(urls["ADD_COMPANY_URL"], wait_until="domcontentloaded")
    page.click("text=Admin")
    assert "User Management" in page.content()
    page.click("text=Add Company")

    # Unique data
    suffix = str(int(time.time()))[-6:]
    company_name = f"AutoTest Company {suffix}"
    company_code = f"CO-{suffix}"

    # Fill form fields
    page.get_by_test_id("name").fill(company_name)
    page.get_by_test_id("code").fill(company_code)

    select_random_measurement(page)
    select_random_partner(page)
    select_random_country(page)
    select_random_currency(page)

    # Submit and validate success message
    page.get_by_role("button", name=re.compile(r"^Add New Company$", re.I)).click()
    expect(page.get_by_text(re.compile(r"The Company has been successfully created", re.I))).to_be_visible()
        
    # Validate newly created company in the view companies list
    #page.goto(urls["VIEW_COMPANIES_URL"], wait_until="domcontentloaded")
    page.click("text=View Companies")
    search = page.get_by_placeholder(re.compile(r"^Search$", re.I))
    search.fill(company_name)
    rows = page.get_by_test_id("table-row")
    target_row = rows.filter(has_text=company_name).first
    expect(target_row).to_be_visible(timeout=15000)
    code_cell = target_row.get_by_test_id("table-cell").nth(2)
    expect(code_cell).to_have_text(company_code)

