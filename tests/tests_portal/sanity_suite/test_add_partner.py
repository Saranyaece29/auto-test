import re, time
from playwright.sync_api import expect
from tests.tests_portal.helpers.user_management_ui import select_random_country 

def test_create_new_partner(login, urls, request):
    page = login
    #page.goto(urls["ADD_PARTNER_URL"], wait_until="domcontentloaded")
    page.click("text=Admin")
    page.click("text=Add Partner")

    # create Unique data
    suffix = str(int(time.time()))[-6:]
    partner_name = f"AutoTest Partner {suffix}"
    partner_code = f"PT-{suffix}"

    # Fill add partner form
    page.get_by_label(re.compile(r"^Name", re.I)).fill(partner_name)
    page.get_by_label(re.compile(r"^Address", re.I)).fill("123 Test Street, Test City, TS 12345")
    page.get_by_label(re.compile(r"^Code", re.I)).fill(partner_code)
    chosen = select_random_country(page)
    print("Picked country:", chosen)

    # Submit and validate success message
    page.get_by_role("button", name=re.compile("^Add New Partner$", re.I)).click()
    expect(page.get_by_text(re.compile(r"The Partner has been successfully created", re.I))).to_be_visible()

    # Validate newly created partner in the view partners list
    page.goto(urls["VIEW_PARTNERS_URL"], wait_until="domcontentloaded")
    search = page.get_by_placeholder("Search")
    search.fill(partner_name)
    rows = page.get_by_test_id("table-row")
    target_row = rows.filter(has_text=partner_name).first
    expect(target_row).to_be_visible(timeout=15000)
    code_cell = target_row.get_by_test_id("table-cell").nth(2)
    expect(code_cell).to_have_text(partner_code)
