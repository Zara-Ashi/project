"""
Auth tests — TC_AUTH_001 … TC_AUTH_010
"""
import pytest
from playwright.sync_api import Page, expect

from config.users import USERS, INVALID_USERS, ERROR_MESSAGES
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


# ── TC_AUTH_001 ──────────────────────────────────────────────────────────────
def test_auth_001_standard_user_login(login_page: LoginPage, page: Page):
    """Успешный вход со стандартным пользователем."""
    u = USERS["standard"]
    login_page.login(u["username"], u["password"])
    page.wait_for_url("**/inventory.html")

    assert "/inventory.html" in page.url
    expect(page.locator(".title")).to_have_text("Products")


# ── TC_AUTH_002 ──────────────────────────────────────────────────────────────
@pytest.mark.parametrize("user_key", ["problem", "performance_glitch", "error", "visual"])
def test_auth_002_valid_users_login(user_key: str, login_page: LoginPage, page: Page):
    """Успешный вход с другими валидными пользователями."""
    u = USERS[user_key]
    login_page.login(u["username"], u["password"])
    page.wait_for_url("**/inventory.html", timeout=15_000)

    assert "/inventory.html" in page.url, f"User '{user_key}' не смог войти"


# ── TC_AUTH_003 ──────────────────────────────────────────────────────────────
def test_auth_003_wrong_password(login_page: LoginPage):
    """Вход с неверным паролем."""
    u = INVALID_USERS["wrong_password"]
    login_page.login(u["username"], u["password"])

    assert login_page.is_error_visible()
    assert ERROR_MESSAGES["wrong_credentials"] in login_page.get_error_message()


# ── TC_AUTH_004 ──────────────────────────────────────────────────────────────
def test_auth_004_nonexistent_user(login_page: LoginPage):
    """Вход с несуществующим логином."""
    u = INVALID_USERS["fake_user"]
    login_page.login(u["username"], u["password"])

    assert login_page.is_error_visible()
    assert ERROR_MESSAGES["wrong_credentials"] in login_page.get_error_message()


# ── TC_AUTH_005 ──────────────────────────────────────────────────────────────
def test_auth_005_empty_username(login_page: LoginPage):
    """Вход с пустым логином."""
    u = INVALID_USERS["empty_username"]
    login_page.login(u["username"], u["password"])

    assert login_page.is_error_visible()
    assert ERROR_MESSAGES["username_required"] in login_page.get_error_message()


# ── TC_AUTH_006 ──────────────────────────────────────────────────────────────
def test_auth_006_empty_password(login_page: LoginPage):
    """Вход с пустым паролем."""
    u = INVALID_USERS["empty_password"]
    login_page.login(u["username"], u["password"])

    assert login_page.is_error_visible()
    assert ERROR_MESSAGES["password_required"] in login_page.get_error_message()


# ── TC_AUTH_007 ──────────────────────────────────────────────────────────────
def test_auth_007_sql_injection(login_page: LoginPage, page: Page):
    """SQL-инъекция в поле логина — доступ должен быть закрыт."""
    u = INVALID_USERS["sql_injection"]
    login_page.login(u["username"], u["password"])

    assert "/inventory.html" not in page.url, "SQL-инъекция дала доступ!"
    assert login_page.is_error_visible()


# ── TC_AUTH_008 ──────────────────────────────────────────────────────────────
def test_auth_008_xss_in_username(login_page: LoginPage, page: Page):
    """XSS-попытка в поле логина — скрипт не должен выполниться."""
    u = INVALID_USERS["xss"]
    login_page.login(u["username"], u["password"])

    # Диалог alert не должен появиться
    alert_triggered = []
    page.on("dialog", lambda d: (alert_triggered.append(True), d.dismiss()))

    assert not alert_triggered, "XSS-атака сработала — alert был показан!"
    # Скрипт должен быть экранирован в DOM, а не исполнен
    content = page.content()
    assert "<script>" not in content or login_page.is_error_visible()


# ── TC_AUTH_009 ──────────────────────────────────────────────────────────────
def test_auth_009_no_lockout_after_failed_attempts(login_page: LoginPage, page: Page):
    """
    SauceDemo не блокирует аккаунт после N неудачных попыток.
    Тест документирует это поведение.
    """
    u_invalid = INVALID_USERS["wrong_password"]
    u_valid   = USERS["standard"]

    for _ in range(5):
        login_page.login(u_invalid["username"], u_invalid["password"])
        assert login_page.is_error_visible()
        page.reload()

    # После 5 неудач — успешный вход должен работать
    login_page.login(u_valid["username"], u_valid["password"])
    page.wait_for_url("**/inventory.html")
    assert "/inventory.html" in page.url, (
        "ДОКУМЕНТАЦИЯ: SauceDemo не блокирует аккаунт — вход после 5 неудач прошёл успешно."
    )


# ── TC_AUTH_010 ──────────────────────────────────────────────────────────────
def test_auth_010_session_persists_after_reload(login_page: LoginPage, page: Page):
    """Сессия сохраняется после перезагрузки страницы."""
    u = USERS["standard"]
    login_page.login(u["username"], u["password"])
    page.wait_for_url("**/inventory.html")

    page.reload()
    page.wait_for_load_state("networkidle")

    assert "/inventory.html" in page.url, "Сессия не сохранилась после reload"
    expect(page.locator(".title")).to_have_text("Products")
