"""
E2E tests — полный цикл покупки
"""
from playwright.sync_api import Page

from config.users import USERS
from config.products import EXPECTED_NAMES, CHECKOUT_INFO
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.complete_page import CompletePage


def test_e2e_full_purchase_flow(page: Page):
    """
    Полный E2E сценарий:
    login → добавить товар → корзина → чекаут → завершение → возврат на главную.
    """
    # 1. Авторизация
    lp = LoginPage(page)
    lp.open()
    lp.login(USERS["standard"]["username"], USERS["standard"]["password"])
    page.wait_for_url("**/inventory.html")

    # 2. Добавить 2 товара
    inv = InventoryPage(page)
    for name in EXPECTED_NAMES[:2]:
        inv.add_to_cart_by_name(name)
    assert inv.get_cart_badge_count() == 2

    # 3. Перейти в корзину
    inv.go_to_cart()
    page.wait_for_url("**/cart.html")

    cart = CartPage(page)
    assert cart.get_item_count() == 2

    # 4. Чекаут шаг 1
    cart.proceed_to_checkout()
    page.wait_for_url("**/checkout-step-one.html")

    chk = CheckoutPage(page)
    info = CHECKOUT_INFO
    chk.fill_info(info["first_name"], info["last_name"], info["postal_code"])
    chk.click_continue()
    page.wait_for_url("**/checkout-step-two.html")

    # 5. Чекаут шаг 2 — проверка суммы
    item_total = chk.get_item_total()
    tax        = chk.get_tax()
    total      = chk.get_total()
    assert abs(total - (item_total + tax)) < 0.01

    chk.click_finish()
    page.wait_for_url("**/checkout-complete.html")

    # 6. Страница успеха
    cp = CompletePage(page)
    assert cp.is_complete_header_visible()
    assert "Thank you" in cp.get_header_text()
    assert cp.is_success_image_visible()

    # 7. Возврат на главную
    cp.go_back_home()
    page.wait_for_url("**/inventory.html")
    assert "/inventory.html" in page.url


def test_e2e_purchase_all_products(page: Page):
    """E2E: купить все 6 товаров за один заказ."""
    lp = LoginPage(page)
    lp.open()
    lp.login(USERS["standard"]["username"], USERS["standard"]["password"])
    page.wait_for_url("**/inventory.html")

    inv = InventoryPage(page)
    for name in EXPECTED_NAMES:
        inv.add_to_cart_by_name(name)
    assert inv.get_cart_badge_count() == 6

    inv.go_to_cart()
    page.wait_for_url("**/cart.html")

    cart = CartPage(page)
    assert cart.get_item_count() == 6

    cart.proceed_to_checkout()
    page.wait_for_url("**/checkout-step-one.html")

    chk = CheckoutPage(page)
    info = CHECKOUT_INFO
    chk.fill_info(info["first_name"], info["last_name"], info["postal_code"])
    chk.click_continue()
    page.wait_for_url("**/checkout-step-two.html")

    assert chk.get_summary_item_count() == 6

    item_total = chk.get_item_total()
    tax        = chk.get_tax()
    total      = chk.get_total()
    assert abs(total - (item_total + tax)) < 0.01

    chk.click_finish()
    page.wait_for_url("**/checkout-complete.html")

    cp = CompletePage(page)
    assert cp.is_complete_header_visible()
