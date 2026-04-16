"""
Генерация отчётов: JSON-summary, консольный вывод, Allure-теги.
"""
import json
import os
import datetime
from typing import Optional


REPORTS_DIR = "output/reports"


# ── JSON-отчёт ────────────────────────────────────────────────────────────────

def save_json_report(data: dict, filename: Optional[str] = None) -> str:
    """
    Сохраняет произвольный словарь в JSON-файл в папке output/reports.

    Args:
        data: данные для сохранения
        filename: имя файла (без расширения). По умолчанию — timestamp.

    Returns:
        Полный путь к файлу.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    if not filename:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{timestamp}"
    path = os.path.join(REPORTS_DIR, f"{filename}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def load_json_report(path: str) -> dict:
    """Загружает JSON-отчёт из файла."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Консольный вывод ──────────────────────────────────────────────────────────

def print_test_summary(results: list[dict]) -> None:
    """
    Выводит сводку результатов тестов в консоль.

    Args:
        results: список словарей с ключами: test_id, name, status, duration_ms, error
    """
    passed  = [r for r in results if r.get("status") == "PASS"]
    failed  = [r for r in results if r.get("status") == "FAIL"]
    skipped = [r for r in results if r.get("status") == "SKIP"]

    total_ms = sum(r.get("duration_ms", 0) for r in results)

    print("\n" + "=" * 70)
    print(f"  ИТОГИ ТЕСТИРОВАНИЯ — {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print(f"  Всего:    {len(results)}")
    print(f"  ✅ Пройдено: {len(passed)}")
    print(f"  ❌ Упало:    {len(failed)}")
    print(f"  ⏭️  Пропущено: {len(skipped)}")
    print(f"  ⏱️  Время:     {total_ms / 1000:.1f}с")
    print("=" * 70)

    if failed:
        print("\n  УПАВШИЕ ТЕСТЫ:")
        for r in failed:
            print(f"  ✗ [{r.get('test_id', '?')}] {r.get('name', '?')}")
            if r.get("error"):
                print(f"      → {r['error'][:120]}")
    print()


def print_performance_report(timings: dict[str, float]) -> None:
    """
    Выводит отчёт по производительности.

    Args:
        timings: словарь {метрика: время_мс}
    """
    print("\n" + "─" * 50)
    print("  ПРОИЗВОДИТЕЛЬНОСТЬ")
    print("─" * 50)
    for name, ms in sorted(timings.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * min(int(ms / 100), 30)
        print(f"  {name:<35} {ms:>7.0f}мс  {bar}")
    print("─" * 50 + "\n")


# ── Allure-теги (декораторы) ─────────────────────────────────────────────────

try:
    import allure

    def allure_step(title: str):
        """Декоратор: оборачивает функцию в allure.step."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                with allure.step(title):
                    return func(*args, **kwargs)
            wrapper.__name__ = func.__name__
            return wrapper
        return decorator

    def attach_screenshot(page, name: str = "screenshot"):
        """Прикрепляет скриншот к Allure-отчёту."""
        allure.attach(
            page.screenshot(),
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )

    def attach_text(text: str, name: str = "log"):
        """Прикрепляет текст к Allure-отчёту."""
        allure.attach(
            text,
            name=name,
            attachment_type=allure.attachment_type.TEXT,
        )

    def attach_json(data: dict, name: str = "data"):
        """Прикрепляет JSON к Allure-отчёту."""
        allure.attach(
            json.dumps(data, ensure_ascii=False, indent=2),
            name=name,
            attachment_type=allure.attachment_type.JSON,
        )

except ImportError:
    # allure не установлен — заглушки
    def allure_step(title: str):
        def decorator(func):
            return func
        return decorator

    def attach_screenshot(page, name: str = "screenshot"):
        pass

    def attach_text(text: str, name: str = "log"):
        pass

    def attach_json(data: dict, name: str = "data"):
        pass


# ── Логирование ───────────────────────────────────────────────────────────────

def log_step(step_number: int, description: str) -> None:
    """Выводит пронумерованный шаг теста в консоль."""
    print(f"  [{step_number:02d}] {description}")


def log_info(message: str) -> None:
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"  [{ts}] ℹ️  {message}")


def log_warning(message: str) -> None:
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"  [{ts}] ⚠️  {message}")


def log_error(message: str) -> None:
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"  [{ts}] ❌ {message}")


def save_run_metadata(
    browser: str,
    total: int,
    passed: int,
    failed: int,
    duration_s: float,
) -> str:
    """Сохраняет метаданные прогона в JSON."""
    data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "browser": browser,
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": total - passed - failed,
        "pass_rate": f"{passed / total * 100:.1f}%" if total else "0%",
        "duration_seconds": round(duration_s, 2),
    }
    return save_json_report(data, filename=f"run_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}")
