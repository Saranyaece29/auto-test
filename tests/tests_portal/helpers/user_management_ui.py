import re, random
from playwright.sync_api import Page, expect

# Be liberal in what we accept as "option" DOM — covers headless UI libs and portals
OPTIONS_SELECTOR = ", ".join([
    "[data-testid='dropdown-option-item']",
    "[role='option']",
    "div[role='listbox'] > *",
    "ul[role='listbox'] li",
    ".rc-virtual-list-holder-inner > *",
])

def _open_menu_and_get_options(page: Page, clickable_area_tid: str, clickable_text_tid: str):
    area = page.get_by_test_id(clickable_area_tid)
    expect(area).to_be_visible()
    area.scroll_into_view_if_needed()

    # Try a few times: menus can animate, render in portals, or attach late
    for _ in range(4):
        area.click()
        opts = page.locator(OPTIONS_SELECTOR)
        try:
            # 1) wait for any option node to be attached
            opts.first.wait_for(state="attached", timeout=1500)
        except Exception:
            # Fallback: some UIs attach the click handler to the label text
            page.get_by_test_id(clickable_text_tid).click()
            try:
                opts.first.wait_for(state="attached", timeout=900)
            except Exception:
                page.wait_for_timeout(120)
                continue

        # 2) give it a beat to become visible (animations)
        try:
            opts.first.wait_for(state="visible", timeout=1200)
        except Exception:
            # Some libs keep items "invisible" during virtual list updates—attached is enough
            pass
        return opts

    raise AssertionError(
        f"Could not open menu for {clickable_area_tid}. "
        f"Check if the menu renders inside an iframe or uses different option markup."
    )

def _pick_random_from_dropdown(
    page: Page,
    *,
    id_suffix: str,           # e.g., "country", "currency", "partner", "measurement"
    placeholder: str,         # e.g., "Select a country" ("" disables filtering of placeholder)
) -> str:
    clickable_area_tid = f"dropdown-clickable-area-{id_suffix}"
    clickable_text_tid = f"dropdown-clickable-text-{id_suffix}"

    options = _open_menu_and_get_options(page, clickable_area_tid, clickable_text_tid)

    # Collect candidate option texts (skip placeholders/empties unless placeholder == "")
    count = options.count()
    names = []
    for i in range(count):
        txt = options.nth(i).inner_text().strip()
        if not txt:
            continue
        if placeholder and txt.lower() == placeholder.lower():
            continue
        names.append(txt)

    # De-dupe while preserving order
    names = list(dict.fromkeys(names))
    assert names, f"No selectable options found (saw {count} nodes) for {id_suffix}"

    choice = random.choice(names)

    # Click exact match (trimmed) to avoid partial matches
    options.filter(has_text=re.compile(rf"^\s*{re.escape(choice)}\s*$")).first.click()

    # Verify the selection reflected in the pill text
    expect(page.get_by_test_id(clickable_text_tid)).to_have_text(
        re.compile(rf"^{re.escape(choice)}$"), timeout=8000
    )
    return choice

# ---------- Public wrappers for each dropdown ----------

def select_random_country(page: Page) -> str:
    return _pick_random_from_dropdown(page, id_suffix="country", placeholder="Select a country")

def select_random_currency(page: Page) -> str:
    # Currency UI shows "£" by default, so we don't exclude a placeholder
    return _pick_random_from_dropdown(page, id_suffix="currency", placeholder="")

def select_random_partner(page: Page) -> str:
    return _pick_random_from_dropdown(page, id_suffix="partner", placeholder="Select a partner")

def select_random_measurement(page: Page) -> str:
    return _pick_random_from_dropdown(page, id_suffix="measurement", placeholder="Select a measurement type")

def select_random_role(page: Page) -> str:
    return _pick_random_from_dropdown(page, id_suffix="role", placeholder="Select a role")

def select_random_country_code(page: Page) -> str:
    # Country code shows a pre-selected value; pick randomly anyway
    return _pick_random_from_dropdown(page, id_suffix="country_code", placeholder="")

def select_random_metric_system(page: Page) -> str:
    # Defaults to "Metric" — pick randomly anyway
    return _pick_random_from_dropdown(page, id_suffix="metric_system", placeholder="")

def select_random_unit(page: Page, unit_suffix: str) -> str:
    # unit_suffix examples: "FlowRateUnit", "LongDistanceUnit", ...
    return _pick_random_from_dropdown(page, id_suffix=f"units-{unit_suffix}", placeholder="")

def _maybe_select_if_visible(page: Page, suffix: str, placeholder: str):
    area = page.get_by_test_id(f"dropdown-clickable-area-{suffix}")

    # allow UI to react to role change
    page.wait_for_timeout(300)

    if area.count() == 0 or not area.is_visible():
        return None

    aria_disabled = (area.get_attribute("aria-disabled") or "").lower() == "true"
    classes = (area.get_attribute("class") or "").lower()
    if aria_disabled or "disabled" in classes or "pointer-events-none" in classes:
        return None

    try:
        return _pick_random_from_dropdown(page, id_suffix=suffix, placeholder=placeholder)
    except AssertionError:
        return None

def maybe_select_random_partner_if_visible(page: Page):
    """For roles that enable 'Partner', select one if the control is visible & enabled."""
    return _maybe_select_if_visible(page, "partner", "Select a partner")

def maybe_select_random_company_if_visible(page: Page):
    """For roles that enable 'Company', select one if the control is visible & enabled."""
    return _maybe_select_if_visible(page, "company", "Select a company")
