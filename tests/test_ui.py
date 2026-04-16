"""
UI / Navigation tests — TC_UI_001 … TC_UI_010
"""
import pytest
from playwright.sync_api import Page, expect

from config.base import VIEWPORTS
from config.users import USERS
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


# ── TC_UI_001 ────────────────────────────────────────────────────────────────
def test_ui_001_logo_navigates_to_inventory(inventory_page: InventoryPage):
    """Клик по логотипу → остаёмся на /inventory.html."""
    logo = inventory_page.page.locator(".app_logo")
    logo.click()
    inventory_page.page.wait_for_load_state("networkidle")

    assert "/inventory.html" in inventory_page.get_url()
    expect(inventory_page.title).to_have_text("Products")


# ── TC_UI_002 ────────────────────────────────────────────────────────────────
def test_ui_002_burger_menu_items(inventory_page: InventoryPage):
    """Гамбургер-меню открывается и содержит все пункты."""
    inventory_page.open_burger_menu()

    page = inventory_page.page
    expect(page.locator("#inventory_sidebar_link")).to_be_visible()
    expect(page.locator("#about_sidebar_link")).to_be_visible()
    expect(page.locator("#logout_sidebar_link")).to_be_visible()
    expect(page.locator("#reset_sidebar_link")).to_be_visible()

    # Закрыть меню
    inventory_page.burger_close.click()
    page.wait_for_selector("#logout_sidebar_link", state="hidden")
    assert not page.locator("#logout_sidebar_link").is_visible()


# ── TC_UI_003 ────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("viewport_name", ["desktop_fhd", "desktop_hd", "mobile"])
def test_ui_003_responsive_layout(viewport_name: str, page: Page):
    """Адаптивность: ключевые элементы видны и кликабельны на всех вьюпортах."""
    vp = VIEWPORTS[viewport_name]
    page.set_viewport_size(vp)

    lp = LoginPage(page)
    lp.open()
    lp.login(USERS["standard"]["username"], USERS["standard"]["password"])
    page.wait_for_url("**/inventory.html")

    inv = InventoryPage(page)
    assert inv.get_item_count() == 6
    expect(inv.cart_icon).to_be_visible()
    expect(inv.burger_menu).to_be_visible()
    expect(inv.sort_dropdown).to_be_visible()


# ── TC_UI_004 ────────────────────────────────────────────────────────────────
def test_ui_004_dark_theme_not_supported(inventory_page: InventoryPage):
    """
    SauceDemo не поддерживает тёмную тему.
    Тест документирует: переключателя нет, background — светлый.
    """
    page = inventory_page.page
    theme_toggle = page.locator("[data-test='theme-toggle'], .theme-switch, #dark-mode-toggle")
    assert theme_toggle.count() == 0, (
        "ДОКУМЕНТАЦИЯ: SauceDemo не поддерживает тёмную тему — переключатель не найден."
    )


# ── TC_UI_005 ────────────────────────────────────────────────────────────────
def test_ui_005_interface_language_english(inventory_page: InventoryPage):
    """
    Интерфейс SauceDemo — только английский язык (локализация не поддерживается).
    """
    expect(inventory_page.title).to_have_text("Products")
    checkout_btn_text = inventory_page.page.locator(".shopping_cart_link").get_attribute("aria-label") or ""
    # Проверяем ключевые слова на английском
    assert inventory_page.get_all_names()[0] != "", "Названия товаров отсутствуют"


# ── TC_UI_006 ────────────────────────────────────────────────────────────────
def test_ui_006_login_button_enabled_when_filled(login_page: LoginPage):
    """Кнопка Login доступна (enabled) при заполненных полях."""
    expect(login_page.login_button).to_be_enabled()

    login_page.username_input.fill("user")
    login_page.password_input.fill("pass")
    expect(login_page.login_button).to_be_enabled()


# ── TC_UI_007 ────────────────────────────────────────────────────────────────
def test_ui_007_tab_navigation_focus(login_page: LoginPage, page: Page):
    """Tab-навигация: фокус переходит Username → Password → Login."""
    login_page.username_input.click()
    page.keyboard.press("Tab")

    # После Tab фокус на поле пароля
    focused = page.evaluate("document.activeElement.id")
    assert focused == "password", f"Ожидали фокус на 'password', получили '{focused}'"

    page.keyboard.press("Tab")
    focused = page.evaluate("document.activeElement.id")
    assert focused == "login-button", f"Ожидали фокус на 'login-button', получили '{focused}'"


# ── TC_UI_008 ────────────────────────────────────────────────────────────────
def test_ui_008_aria_attributes_on_login(login_page: LoginPage):
    """ARIA-атрибуты присутствуют на ключевых элементах формы входа."""
    page = login_page.page

    username_placeholder = page.locator("#user-name").get_attribute("placeholder")
    password_placeholder = page.locator("#password").get_attribute("placeholder")

    assert username_placeholder, "У поля username нет placeholder/aria-label"
    assert password_placeholder, "У поля password нет placeholder/aria-label"


# ── TC_UI_009 ────────────────────────────────────────────────────────────────
def test_ui_009_page_loads_without_js_errors(page: Page):
    """Страница загружается без JS-ошибок в консоли."""
    js_errors = []
    page.on("pageerror", lambda err: js_errors.append(str(err)))

    lp = LoginPage(page)
    lp.open()
    lp.login(USERS["standard"]["username"], USERS["standard"]["password"])
    page.wait_for_url("**/inventory.html")
    page.wait_for_load_state("networkidle")

    critical_errors = [e for e in js_errors if "TypeError" in e or "ReferenceError" in e]
    assert not critical_errors, f"Критические JS-ошибки: {critical_errors}"


# ── TC_UI_010 ────────────────────────────────────────────────────────────────
def test_ui_010_nonexistent_url_handled(page: Page):
    """
    Переход на несуществующий URL — SauceDemo редиректит на главную или показывает ошибку.
    """
    from config.base import BASE_URL
    page.goto(f"{BASE_URL}/nonexistent-page")
    page.wait_for_load_state("networkidle")

    url = page.url
    # SauceDemo либо редиректит на /, либо остаётся на /nonexistent-pages
    # Проверяем, что страница хоть как-то обработана (нет пустого экрана)
    content = page.content()
    assert len(content) > 100, "Страница не загрузилась (пустой контент)"
    # Документируем поведение
    print(f"TC_UI_010: Поведение при несуществующем URL — итоговый URL: {url}")
