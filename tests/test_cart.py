"""
Cart tests — TC_CART_001 … TC_CART_010
"""
import pytest
from playwright.sync_api import Page, expect

from config.products import EXPECTED_NAMES
from config.users import USERS
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.login_page import LoginPage


# ── TC_CART_001 ──────────────────────────────────────────────────────────────
def test_cart_001_add_one_item(inventory_page: InventoryPage):
    """Добавление одного товара — бейдж = 1."""
    inventory_page.add_to_cart_by_name(EXPECTED_NAMES[0])
    assert inventory_page.get_cart_badge_count() == 1


# ── TC_CART_002 ──────────────────────────────────────────────────────────────
def test_cart_002_add_multiple_items(inventory_page: InventoryPage):
    """Добавление 3 разных товаров — бейдж = 3."""
    for name in EXPECTED_NAMES[:3]:
        inventory_page.add_to_cart_by_name(name)
    assert inventory_page.get_cart_badge_count() == 3


# ── TC_CART_003 ──────────────────────────────────────────────────────────────
def test_cart_003_add_same_item_once(inventory_page: InventoryPage):

    product = EXPECTED_NAMES[0]
    inventory_page.add_to_cart_by_name(product)

    btn_text = inventory_page.get_button_text_by_name(product)
    assert btn_text.lower() == "remove", "Кнопка не сменилась на Remove"
    assert inventory_page.get_cart_badge_count() == 1


# ── TC_CART_004 ──────────────────────────────────────────────────────────────
def test_cart_004_remove_item(inventory_page: InventoryPage):
    """Добавить товар → Remove → бейдж = 0, товар исчез из корзины."""
    product = EXPECTED_NAMES[0]
    inventory_page.add_to_cart_by_name(product)
    assert inventory_page.get_cart_badge_count() == 1

    inventory_page.remove_from_cart_by_name(product)
    assert inventory_page.get_cart_badge_count() == 0


# ── TC_CART_005 ──────────────────────────────────────────────────────────────
def test_cart_005_no_quantity_controls(inventory_page: InventoryPage, cart_page: CartPage):
    inventory_page.add_to_cart_by_name(EXPECTED_NAMES[0])
    inventory_page.go_to_cart()
    inventory_page.page.wait_for_url("**/cart.html")

    qty_elements = inventory_page.page.locator(".cart_quantity").all_inner_texts()
    for qty in qty_elements:
        assert qty == "1", f"Ожидали qty=1, получили '{qty}'"


# ── TC_CART_006 ──────────────────────────────────────────────────────────────
def test_cart_006_navigate_to_cart_from_inventory(inventory_page: InventoryPage):
    """Клик по иконке корзины → переход на /cart.html."""
    inventory_page.add_to_cart_by_name(EXPECTED_NAMES[0])
    inventory_page.go_to_cart()
    inventory_page.page.wait_for_url("**/cart.html")

    assert "/cart.html" in inventory_page.get_url()


# ── TC_CART_007 ──────────────────────────────────────────────────────────────
def test_cart_007_continue_shopping_returns_to_inventory(
    inventory_page: InventoryPage, cart_page: CartPage
):
    """'Continue Shopping' из корзины → возврат на /inventory.html."""
    inventory_page.go_to_cart()
    inventory_page.page.wait_for_url("**/cart.html")
    cart_page.continue_shopping_click()
    inventory_page.page.wait_for_url("**/inventory.html")

    assert "/inventory.html" in inventory_page.get_url()


# ── TC_CART_008 ──────────────────────────────────────────────────────────────
def test_cart_008_empty_cart(inventory_page: InventoryPage, cart_page: CartPage):
    """Открыть корзину без добавления товаров — корзина пустая."""
    inventory_page.go_to_cart()
    inventory_page.page.wait_for_url("**/cart.html")

    assert cart_page.is_empty(), "Корзина должна быть пустой"


# ── TC_CART_009 ──────────────────────────────────────────────────────────────
def test_cart_009_cart_persists_after_reload(
    inventory_page: InventoryPage, cart_page: CartPage
):
    """Корзина сохраняется после перезагрузки страницы."""
    product = EXPECTED_NAMES[0]
    inventory_page.add_to_cart_by_name(product)
    assert inventory_page.get_cart_badge_count() == 1

    inventory_page.page.reload()
    inventory_page.page.wait_for_load_state("networkidle")

    assert inventory_page.get_cart_badge_count() == 1, "Корзина не сохранилась после reload"