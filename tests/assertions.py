
from typing import List


def assert_url_contains(url: str, expected_part: str, context: str = ""):
    """Проверяет, что URL содержит ожидаемую подстроку."""
    assert expected_part in url, (
        f"{context + ': ' if context else ''}URL '{url}' не содержит '{expected_part}'"
    )


def assert_prices_ascending(prices: List[float], context: str = ""):
    """Проверяет, что цены отсортированы по возрастанию."""
    for i in range(len(prices) - 1):
        assert prices[i] <= prices[i + 1], (
            f"{context + ': ' if context else ''}"
            f"Цены не по возрастанию: {prices[i]} > {prices[i + 1]} "
            f"(индексы {i} и {i + 1})\nПолный список: {prices}"
        )


def assert_prices_descending(prices: List[float], context: str = ""):
    """Проверяет, что цены отсортированы по убыванию."""
    for i in range(len(prices) - 1):
        assert prices[i] >= prices[i + 1], (
            f"{context + ': ' if context else ''}"
            f"Цены не по убыванию: {prices[i]} < {prices[i + 1]} "
            f"(индексы {i} и {i + 1})\nПолный список: {prices}"
        )


def assert_names_alphabetical(names: List[str], context: str = ""):
    """Проверяет алфавитный порядок названий (A→Z)."""
    for i in range(len(names) - 1):
        assert names[i].lower() <= names[i + 1].lower(), (
            f"{context + ': ' if context else ''}"
            f"Названия не по алфавиту: '{names[i]}' > '{names[i + 1]}' "
            f"(индексы {i} и {i + 1})"
        )


def assert_total_correct(item_total: float, tax: float, total: float,
                          tolerance: float = 0.01, context: str = ""):
    """Проверяет: Total = Item total + Tax (с допустимой погрешностью)."""
    expected = item_total + tax
    assert abs(total - expected) < tolerance, (
        f"{context + ': ' if context else ''}"
        f"Итог {total:.2f} ≠ товары {item_total:.2f} + налог {tax:.2f} = {expected:.2f} "
        f"(разница {abs(total - expected):.4f} > {tolerance})"
    )


def assert_cart_count(actual: int, expected: int, context: str = ""):
    """Проверяет количество товаров в корзине."""
    assert actual == expected, (
        f"{context + ': ' if context else ''}"
        f"Корзина: ожидали {expected} товар(ов), получили {actual}"
    )


def assert_error_message_contains(actual: str, expected_fragment: str, context: str = ""):
    """Проверяет, что сообщение об ошибке содержит нужный текст."""
    assert expected_fragment in actual, (
        f"{context + ': ' if context else ''}"
        f"Сообщение об ошибке '{actual}' не содержит '{expected_fragment}'"
    )


def assert_list_equals_unordered(actual: List, expected: List, label: str = "Список"):
    """Проверяет совпадение двух списков независимо от порядка."""
    assert sorted(actual) == sorted(expected), (
        f"{label} не совпадает:\n"
        f"  Фактический:  {sorted(actual)}\n"
        f"  Ожидаемый:    {sorted(expected)}\n"
        f"  Лишние:       {set(actual) - set(expected)}\n"
        f"  Отсутствующие:{set(expected) - set(actual)}"
    )


def assert_images_not_broken(natural_widths: List[int], context: str = ""):
    """Проверяет, что все изображения не битые (naturalWidth > 0)."""
    broken = [i for i, w in enumerate(natural_widths) if w == 0]
    assert not broken, (
        f"{context + ': ' if context else ''}"
        f"Битые изображения (naturalWidth == 0) на индексах: {broken}"
    )


def assert_page_load_time(elapsed_ms: float, threshold_ms: float, page_name: str = "Страница"):
    """Проверяет время загрузки страницы."""
    assert elapsed_ms < threshold_ms, (
        f"{page_name} загружалась {elapsed_ms:.0f}мс, "
        f"что превышает порог {threshold_ms:.0f}мс"
    )
