"""
Checkout tests — TC_CHECK_001 … TC_CHECK_010
"""
import pytest
from playwright.sync_api import Page

from config.products import EXPECTED_NAMES, CHECKOUT_INFO
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.complete_page import CompletePage


def _add_product_and_go_to_checkout(inventory_page, cart_page, checkout_page, n=1):
    """Вспомогательная функция: добавить n товаров → перейти к чекауту."""
    for name in EXPECTED_NAMES[:n]:
        inventory_page.add_to_cart_by_name(name)
    inventory_page.go_to_cart()
    inventory_page.page.wait_for_url("**/cart.html")
    cart_page.proceed_to_checkout()
    inventory_page.page.wait_for_url("**/checkout-step-one.html")


# ── TC_CHECK_001 ─────────────────────────────────────────────────────────────
def test_check_001_full_successful_checkout(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
    complete_page: CompletePage,
):
    """Полный успешный чекаут от добавления товара до страницы завершения."""
    _add_product_and_go_to_checkout(inventory_page, cart_page, checkout_page)

    info = CHECKOUT_INFO
    checkout_page.fill_info(info["first_name"], info["last_name"], info["postal_code"])
    checkout_page.click_continue()
    inventory_page.page.wait_for_url("**/checkout-step-two.html")

    checkout_page.click_finish()
    inventory_page.page.wait_for_url("**/checkout-complete.html")

    assert complete_page.is_complete_header_visible()
    assert "Thank you" in complete_page.get_header_text()


# ── TC_CHECK_002 ─────────────────────────────────────────────────────────────
def test_check_002_empty_first_name(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
):
    """Чекаут с пустым First name — ошибка валидации."""
    _add_product_and_go_to_checkout(inventory_page, cart_page, checkout_page)

    checkout_page.fill_info("", CHECKOUT_INFO["last_name"], CHECKOUT_INFO["postal_code"])
    checkout_page.click_continue()

    assert checkout_page.is_error_visible()
    assert "First Name is required" in checkout_page.get_error_message()


# ── TC_CHECK_003 ─────────────────────────────────────────────────────────────
def test_check_003_empty_last_name(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
):
    """Чекаут с пустым Last name — ошибка валидации."""
    _add_product_and_go_to_checkout(inventory_page, cart_page, checkout_page)

    checkout_page.fill_info(CHECKOUT_INFO["first_name"], "", CHECKOUT_INFO["postal_code"])
    checkout_page.click_continue()

    assert checkout_page.is_error_visible()
    assert "Last Name is required" in checkout_page.get_error_message()


# ── TC_CHECK_004 ─────────────────────────────────────────────────────────────
def test_check_004_empty_postal_code(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
):
    """Чекаут с пустым Postal code — ошибка валидации."""
    _add_product_and_go_to_checkout(inventory_page, cart_page, checkout_page)

    checkout_page.fill_info(CHECKOUT_INFO["first_name"], CHECKOUT_INFO["last_name"], "")
    checkout_page.click_continue()

    assert checkout_page.is_error_visible()
    assert "Postal Code is required" in checkout_page.get_error_message()


# ── TC_CHECK_005 ─────────────────────────────────────────────────────────────
def test_check_005_postal_code_accepts_any_format(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
):
    """
    SauceDemo принимает любой формат Postal code (буквы, цифры, спецсимволы).
    Тест документирует отсутствие валидации формата.
    """
    _add_product_and_go_to_checkout(inventory_page, cart_page, checkout_page)

    checkout_page.fill_info(
        CHECKOUT_INFO["first_name"], CHECKOUT_INFO["last_name"], "ABC!@#"
    )
    checkout_page.click_continue()

    page = inventory_page.page
    # Ожидаем переход на шаг 2 — значит сайт принял любой формат
    assert "/checkout-step-two.html" in page.url, (
        "ДОКУМЕНТАЦИЯ: SauceDemo не валидирует формат Postal code"
    )


# ── TC_CHECK_006 ─────────────────────────────────────────────────────────────
def test_check_006_cancel_step1_returns_to_cart(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
):
    """Cancel на шаге 1 → возврат в корзину."""
    _add_product_and_go_to_checkout(inventory_page, cart_page, checkout_page)
    checkout_page.click_cancel()
    inventory_page.page.wait_for_url("**/cart.html")

    assert "/cart.html" in inventory_page.get_url()
    assert not cart_page.is_empty(), "Товары должны остаться в корзине"


# ── TC_CHECK_007 ─────────────────────────────────────────────────────────────
def test_check_007_cancel_then_continue_shopping(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
):
    """Cancel → Continue Shopping → возврат на inventory."""
    _add_product_and_go_to_checkout(inventory_page, cart_page, checkout_page)
    checkout_page.click_cancel()
    inventory_page.page.wait_for_url("**/cart.html")

    cart_page.continue_shopping_click()
    inventory_page.page.wait_for_url("**/inventory.html")

    assert "/inventory.html" in inventory_page.get_url()


# ── TC_CHECK_008 ─────────────────────────────────────────────────────────────
def test_check_008_total_equals_item_plus_tax(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
):
    """Итог = сумма товаров + налог (погрешность < 1 цент)."""
    _add_product_and_go_to_checkout(inventory_page, cart_page, checkout_page)

    info = CHECKOUT_INFO
    checkout_page.fill_info(info["first_name"], info["last_name"], info["postal_code"])
    checkout_page.click_continue()
    inventory_page.page.wait_for_url("**/checkout-step-two.html")

    item_total = checkout_page.get_item_total()
    tax        = checkout_page.get_tax()
    total      = checkout_page.get_total()

    assert abs(total - (item_total + tax)) < 0.01, (
        f"Итог {total} ≠ товары {item_total} + налог {tax}"
    )


# ── TC_CHECK_009 ─────────────────────────────────────────────────────────────
def test_check_009_total_rounded_to_two_decimals(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
):
    """Итоговая сумма округлена до 2 знаков после запятой."""
    _add_product_and_go_to_checkout(inventory_page, cart_page, checkout_page)

    info = CHECKOUT_INFO
    checkout_page.fill_info(info["first_name"], info["last_name"], info["postal_code"])
    checkout_page.click_continue()
    inventory_page.page.wait_for_url("**/checkout-step-two.html")

    total = checkout_page.get_total()
    rounded = round(total, 2)
    assert total == rounded, f"Итог {total} не округлён до 2 знаков"


# ── TC_CHECK_010 ─────────────────────────────────────────────────────────────
def test_check_010_checkout_with_multiple_items(
    inventory_page: InventoryPage,
    cart_page: CartPage,
    checkout_page: CheckoutPage,
    complete_page: CompletePage,
):
    """Чекаут с 2 товарами — сумма корректна, оба товара в заказе."""
    _add_product_and_go_to_checkout(inventory_page, cart_page, checkout_page, n=2)

    info = CHECKOUT_INFO
    checkout_page.fill_info(info["first_name"], info["last_name"], info["postal_code"])
    checkout_page.click_continue()
    inventory_page.page.wait_for_url("**/checkout-step-two.html")

    assert checkout_page.get_summary_item_count() == 2

    item_total = checkout_page.get_item_total()
    tax        = checkout_page.get_tax()
    total      = checkout_page.get_total()
    assert abs(total - (item_total + tax)) < 0.01

    checkout_page.click_finish()
    inventory_page.page.wait_for_url("**/checkout-complete.html")
    assert complete_page.is_complete_header_visible()
