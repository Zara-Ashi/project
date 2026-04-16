"""
Cross-browser / cross-platform tests — TC_XB_001 … TC_XB_005

Запуск по браузерам через pytest-playwright:
  pytest tests/test_cross_browser.py --browser chromium
  pytest tests/test_cross_browser.py --browser firefox
  pytest tests/test_cross_browser.py --browser webkit
  pytest tests/test_cross_browser.py --browser chromium --browser firefox --browser webkit
"""
import pytest
from playwright.sync_api import Page, expect

from config.base import VIEWPORTS
from config.users import USERS
from config.products import EXPECTED_NAMES, CHECKOUT_INFO
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.complete_page import CompletePage


def _full_login(page: Page) -> InventoryPage:
    lp = LoginPage(page)
    lp.open()
    lp.login(USERS["standard"]["username"], USERS["standard"]["password"])
    page.wait_for_url("**/inventory.html")
    return InventoryPage(page)


# ── TC_XB_001/002/003: параметризуются снаружи через --browser ───────────────
def test_xb_basic_scenario(page: Page):
    """
    TC_XB_001 (Chromium) / TC_XB_002 (Firefox) / TC_XB_003 (WebKit)
    Базовый сценарий: login → 6 товаров → добавить в корзину → чекаут → успех.
    Запускать с нужным --browser флагом.
    """
    inv = _full_login(page)
    assert inv.get_item_count() == 6

    inv.add_to_cart_by_name(EXPECTED_NAMES[0])
    assert inv.get_cart_badge_count() == 1

    inv.go_to_cart()
    page.wait_for_url("**/cart.html")

    cart = CartPage(page)
    cart.proceed_to_checkout()
    page.wait_for_url("**/checkout-step-one.html")

    chk = CheckoutPage(page)
    info = CHECKOUT_INFO
    chk.fill_info(info["first_name"], info["last_name"], info["postal_code"])
    chk.click_continue()
    page.wait_for_url("**/checkout-step-two.html")
    chk.click_finish()
    page.wait_for_url("**/checkout-complete.html")

    cp = CompletePage(page)
    assert cp.is_complete_header_visible()
    assert "Thank you" in cp.get_header_text()


# ── TC_XB_004 ────────────────────────────────────────────────────────────────
def test_xb_004_headless_headed_same_result(page: Page):
    """
    Headless vs Headed: результат одинаков.
    Сам тест идентичен — режим задаётся снаружи (--headed / по умолчанию headless).
    """
    inv = _full_login(page)
    assert inv.get_item_count() == 6

    names = inv.get_all_names()
    assert len(names) == 6
    assert all(len(n) > 0 for n in names), "Пустые названия товаров в headless/headed режиме"


# ── TC_XB_005 ────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("viewport_name,expected_items", [
    ("desktop_fhd", 6),
    ("desktop_hd",  6),
    ("mobile",      6),
])
def test_xb_005_different_resolutions(
    viewport_name: str, expected_items: int, page: Page
):
    """
    TC_XB_005: Разные разрешения экрана — UI не ломается, все элементы доступны.
    1920×1080, 1366×768, 375×667 (mobile).
    """
    vp = VIEWPORTS[viewport_name]
    page.set_viewport_size(vp)

    inv = _full_login(page)

    # Все товары отображаются
    assert inv.get_item_count() == expected_items, (
        f"[{viewport_name}] Ожидали {expected_items} товаров"
    )

    # Ключевые элементы видны
    expect(inv.cart_icon).to_be_visible()
    expect(inv.burger_menu).to_be_visible()
    expect(inv.sort_dropdown).to_be_visible()
    expect(inv.title).to_have_text("Products")

    # Кнопки товаров кликабельны
    first_item_btn = page.locator(".inventory_item button").first
    expect(first_item_btn).to_be_visible()
    expect(first_item_btn).to_be_enabled()
