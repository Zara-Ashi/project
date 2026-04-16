"""
Вспомогательные утилиты: форматирование цен, ожидание элементов, генерация данных.
"""
import re
import time
import random
import string
from typing import Optional, Callable

from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError


# ── Форматирование цен ────────────────────────────────────────────────────────

def parse_price(price_text: str) -> float:
    """
    Преобразует строку цены в float.
    Примеры: '$29.99' → 29.99, 'Item total: $45.98' → 45.98
    """
    match = re.search(r"\$?([\d]+\.[\d]{1,2})", price_text)
    if not match:
        raise ValueError(f"Не удалось распарсить цену из: '{price_text}'")
    return float(match.group(1))


def format_price(value: float) -> str:
    """Форматирует float в строку цены: 29.99 → '$29.99'"""
    return f"${value:.2f}"


def calculate_expected_total(prices: list[float], tax_rate: float = 0.08) -> dict:
    """
    Рассчитывает ожидаемые суммы заказа.

    Returns:
        dict с ключами: item_total, tax, total
    """
    item_total = round(sum(prices), 2)
    tax = round(item_total * tax_rate, 2)
    total = round(item_total + tax, 2)
    return {"item_total": item_total, "tax": tax, "total": total}


# ── Ожидание элементов ────────────────────────────────────────────────────────

def wait_for_element(
    page: Page,
    selector: str,
    timeout_ms: int = 10_000,
    state: str = "visible"
) -> bool:
    """
    Ожидает появления элемента. Возвращает True при успехе, False при таймауте.
    """
    try:
        page.wait_for_selector(selector, timeout=timeout_ms, state=state)
        return True
    except PlaywrightTimeoutError:
        return False


def wait_for_url_change(page: Page, original_url: str, timeout_ms: int = 10_000) -> bool:
    """Ждёт, пока URL изменится."""
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        if page.url != original_url:
            return True
        time.sleep(0.1)
    return False


def wait_for_condition(
    condition: Callable[[], bool],
    timeout_ms: int = 10_000,
    poll_interval_ms: int = 100,
    message: str = "Условие не выполнено"
) -> None:
    """Ожидает выполнения произвольного условия."""
    deadline = time.monotonic() + timeout_ms / 1000
    while time.monotonic() < deadline:
        if condition():
            return
        time.sleep(poll_interval_ms / 1000)
    raise TimeoutError(f"{message} (таймаут {timeout_ms}мс)")


# ── Генерация тестовых данных ─────────────────────────────────────────────────

def random_string(length: int = 8) -> str:
    """Генерирует случайную строку из букв."""
    return "".join(random.choices(string.ascii_letters, k=length))


def random_postal_code(digits: int = 5) -> str:
    """Генерирует случайный почтовый индекс."""
    return "".join(random.choices(string.digits, k=digits))


def random_checkout_info() -> dict:
    """Генерирует случайные данные для чекаута."""
    return {
        "first_name": random_string(6).capitalize(),
        "last_name":  random_string(8).capitalize(),
        "postal_code": random_postal_code(),
    }


# ── Работа с элементами ───────────────────────────────────────────────────────

def get_all_texts(locator: Locator) -> list[str]:
    """Возвращает текст всех элементов локатора (очищенный)."""
    return [t.strip() for t in locator.all_inner_texts()]


def get_all_prices_from_locator(locator: Locator) -> list[float]:
    """Парсит цены из всех элементов локатора."""
    texts = get_all_texts(locator)
    return [parse_price(t) for t in texts]


def check_image_loaded(page: Page, img_locator: Locator) -> bool:
    """Проверяет, что изображение загружено (naturalWidth > 0)."""
    return img_locator.evaluate("el => el.naturalWidth > 0")


# ── Измерение времени ─────────────────────────────────────────────────────────

class Timer:
    """Контекстный менеджер для измерения времени выполнения."""

    def __init__(self):
        self.elapsed_ms: float = 0.0
        self._start: float = 0.0

    def __enter__(self):
        self._start = time.monotonic()
        return self

    def __exit__(self, *args):
        self.elapsed_ms = (time.monotonic() - self._start) * 1000

    def __str__(self):
        return f"{self.elapsed_ms:.0f}мс"


# ── Скриншоты ────────────────────────────────────────────────────────────────

def take_screenshot(page: Page, name: str, folder: str = "output/screenshots") -> str:
    """Делает скриншот и возвращает путь к файлу."""
    import os
    os.makedirs(folder, exist_ok=True)
    path = f"{folder}/{name}.png"
    page.screenshot(path=path)
    return path


def take_fullpage_screenshot(page: Page, name: str, folder: str = "output/screenshots") -> str:
    """Делает полностраничный скриншот."""
    import os
    os.makedirs(folder, exist_ok=True)
    path = f"{folder}/{name}_full.png"
    page.screenshot(path=path, full_page=True)
    return path
