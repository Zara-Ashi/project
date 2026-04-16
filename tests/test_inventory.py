"""
Inventory tests — TC_INV_001 … TC_INV_010
"""
import pytest
from playwright.sync_api import expect

from config.products import EXPECTED_NAMES, EXPECTED_PRICES
from pages.inventory_page import InventoryPage


# ── TC_INV_001 ───────────────────────────────────────────────────────────────
def test_inv_001_all_six_products_displayed(inventory_page: InventoryPage):
    """На странице отображаются ровно 6 товаров."""
    assert inventory_page.get_item_count() == 6


# ── TC_INV_002 ───────────────────────────────────────────────────────────────
def test_inv_002_product_names_match(inventory_page: InventoryPage):
    """Названия товаров совпадают с эталонным списком."""
    actual_names = sorted(inventory_page.get_all_names())
    expected     = sorted(EXPECTED_NAMES)
    assert actual_names == expected, f"Имена не совпадают:\n{actual_names}\nvs\n{expected}"


# ── TC_INV_003 ───────────────────────────────────────────────────────────────
def test_inv_003_product_prices_match(inventory_page: InventoryPage):
    """Цены товаров соответствуют эталону."""
    actual_prices = sorted(inventory_page.get_all_prices())
    expected      = sorted(EXPECTED_PRICES)
    assert actual_prices == expected, f"Цены не совпадают: {actual_prices} vs {expected}"

# ── TC_INV_005 ───────────────────────────────────────────────────────────────
def test_inv_005_sort_price_low_to_high(inventory_page: InventoryPage):
    """Сортировка по цене: низкая → высокая."""
    inventory_page.sort_by("lohi")
    prices = inventory_page.get_all_prices()
    assert prices == sorted(prices), f"Цены не по возрастанию: {prices}"


# ── TC_INV_006 ───────────────────────────────────────────────────────────────
def test_inv_006_sort_price_high_to_low(inventory_page: InventoryPage):
    """Сортировка по цене: высокая → низкая."""
    inventory_page.sort_by("hilo")
    prices = inventory_page.get_all_prices()
    assert prices == sorted(prices, reverse=True), f"Цены не по убыванию: {prices}"


# ── TC_INV_007 ───────────────────────────────────────────────────────────────
def test_inv_007_sort_name_a_to_z(inventory_page: InventoryPage):
    """Сортировка по названию: A → Z."""
    inventory_page.sort_by("az")
    names = inventory_page.get_all_names()
    assert names == sorted(names), f"Имена не по алфавиту: {names}"


# ── TC_INV_008 ───────────────────────────────────────────────────────────────
def test_inv_008_item_stays_in_cart_after_sort(inventory_page: InventoryPage):
    """Товар в корзине не теряется при смене сортировки."""
    first_product = EXPECTED_NAMES[0]
    inventory_page.add_to_cart_by_name(first_product)
    assert inventory_page.get_cart_badge_count() == 1

    inventory_page.sort_by("hilo")
    assert inventory_page.get_cart_badge_count() == 1

    inventory_page.sort_by("az")
    assert inventory_page.get_cart_badge_count() == 1


# ── TC_INV_009 ───────────────────────────────────────────────────────────────
def test_inv_009_click_item_image_navigates(inventory_page: InventoryPage):
    """Клик по изображению товара переходит на страницу детального просмотра."""
    inventory_page.click_item_image(0)
    inventory_page.page.wait_for_load_state("networkidle")

    url = inventory_page.get_url()
    assert "inventory-item" in url or "item" in url, (
        f"Не перешли на страницу товара. Текущий URL: {url}"
    )


# ── TC_INV_010 ───────────────────────────────────────────────────────────────
def test_inv_010_remove_button_and_cart_badge(inventory_page: InventoryPage):
    """Add → кнопка меняется на Remove → нажать → бейдж = 0."""
    product = EXPECTED_NAMES[0]

    # Добавить
    inventory_page.add_to_cart_by_name(product)
    btn_text = inventory_page.get_button_text_by_name(product)
    assert btn_text.lower() == "remove", f"Ожидали 'Remove', получили '{btn_text}'"
    assert inventory_page.get_cart_badge_count() == 1

    # Удалить
    inventory_page.remove_from_cart_by_name(product)
    assert inventory_page.get_cart_badge_count() == 0
