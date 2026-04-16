"""
Performance tests — TC_PERF_001 … TC_PERF_005
"""
import time
import pytest
from playwright.sync_api import Page, BrowserContext

from config.base import BASE_URL, PERFORMANCE
from config.users import USERS
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage


def _login(page: Page):
    lp = LoginPage(page)
    lp.open()
    lp.login(USERS["standard"]["username"], USERS["standard"]["password"])
    page.wait_for_url("**/inventory.html")
    return InventoryPage(page)


# ── TC_PERF_001 ──────────────────────────────────────────────────────────────
def test_perf_001_inventory_page_load_time(page: Page):
    """Время загрузки главной страницы < 3 секунды."""
    lp = LoginPage(page)
    lp.open()
    lp.login(USERS["standard"]["username"], USERS["standard"]["password"])

    start = time.monotonic()
    page.wait_for_url("**/inventory.html")
    page.wait_for_load_state("networkidle")
    elapsed_ms = (time.monotonic() - start) * 1000

    assert elapsed_ms < PERFORMANCE["page_load_threshold_ms"], (
        f"Страница загружалась {elapsed_ms:.0f}мс > {PERFORMANCE['page_load_threshold_ms']}мс"
    )


# ── TC_PERF_002 ──────────────────────────────────────────────────────────────
def test_perf_002_login_button_response_time(page: Page):
    """Кнопка Login → переход на inventory < 1 секунды."""
    lp = LoginPage(page)
    lp.open()
    lp.username_input.fill(USERS["standard"]["username"])
    lp.password_input.fill(USERS["standard"]["password"])

    start = time.monotonic()
    lp.login_button.click()
    page.wait_for_url("**/inventory.html")
    elapsed_ms = (time.monotonic() - start) * 1000

    assert elapsed_ms < PERFORMANCE["button_response_ms"], (
        f"Переход занял {elapsed_ms:.0f}мс > {PERFORMANCE['button_response_ms']}мс"
    )


# ── TC_PERF_003 ──────────────────────────────────────────────────────────────
@pytest.mark.parametrize("run", range(1, 6))
def test_perf_003_stability_repeated_runs(run: int, page: Page):
    """Базовый сценарий стабильно проходит при повторных запусках (5/5)."""
    inv = _login(page)
    assert inv.get_item_count() == 6, f"Прогон {run}: товары не загрузились"
    assert inv.get_cart_badge_count() == 0, f"Прогон {run}: корзина не пустая"


# ── TC_PERF_004 ──────────────────────────────────────────────────────────────
def test_perf_004_slow_network_throttling(context: BrowserContext):
    """
    Сценарий при медленном соединении (эмуляция Slow 3G).
    Таймаут увеличен до 60 секунд.
    """
    # Эмуляция медленной сети
    context.set_default_timeout(60_000)

    page = context.new_page()

    # Playwright CDPSession для throttling
    client = page.context.new_cdp_session(page)
    client.send("Network.enable", {})
    client.send("Network.emulateNetworkConditions", {
        "offline": False,
        "downloadThroughput": 50 * 1024 / 8,   # 50 kbps
        "uploadThroughput": 20 * 1024 / 8,      # 20 kbps
        "latency": 2000,                         # 2000ms RTT
    })

    lp = LoginPage(page)
    lp.open()
    lp.login(USERS["standard"]["username"], USERS["standard"]["password"])
    page.wait_for_url("**/inventory.html", timeout=60_000)

    inv = InventoryPage(page)
    assert inv.get_item_count() == 6, "Страница не загрузилась при медленной сети"

    # Отключить throttling
    client.send("Network.emulateNetworkConditions", {
        "offline": False,
        "downloadThroughput": -1,
        "uploadThroughput": -1,
        "latency": 0,
    })
    page.close()


# ── TC_PERF_005 ──────────────────────────────────────────────────────────────
def test_perf_005_memory_leak_multiple_navigations(page: Page):
    """
    Нет критических утечек памяти при многократной навигации по страницам.
    Проверяем через JS performance.memory (только Chromium).
    """
    inv = _login(page)

    try:
        mem_before = page.evaluate(
            "() => performance.memory ? performance.memory.usedJSHeapSize : null"
        )
    except Exception:
        pytest.skip("performance.memory недоступен в этом браузере")
        return

    if mem_before is None:
        pytest.skip("performance.memory недоступен (не Chromium)")
        return

    # Навигация по страницам товаров и обратно (10 итераций)
    for _ in range(10):
        inv.cart_icon.click()
        page.wait_for_url("**/cart.html")
        page.go_back()
        page.wait_for_url("**/inventory.html")

    mem_after = page.evaluate("() => performance.memory.usedJSHeapSize")
    growth_percent = ((mem_after - mem_before) / mem_before) * 100

    assert growth_percent < 20, (
        f"Память выросла на {growth_percent:.1f}% > 20% после 10 навигаций"
    )
