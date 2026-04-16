# saucedemo-playwright-tests

Учебный проект автоматизации тестирования сайта [SauceDemo](https://www.saucedemo.com)
с использованием **Playwright + pytest** и паттерна **Page Object Model**.

---

## Структура проекта

```
saucedemo-playwright-tests/
├── config/               # URL, пользователи, данные товаров
├── pages/                # Page Object Model (POM)
├── tests/                # Тест-кейсы (58 тестов)
├── utils/                # Хелперы, assertions, reporter
├── data/                 # JSON с эталонными данными
├── output/               # Скриншоты, видео, логи, отчёты
├── conftest.py           # Фикстуры pytest
├── pytest.ini            # Конфигурация pytest
└── requirements.txt      # Зависимости
```

---

## Установка

### 1. Клонировать / перейти в папку проекта

```powershell
cd saucedemo-playwright-tests
```

### 2. Создать виртуальное окружение (рекомендуется)

```powershell
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS
```

### 3. Установить зависимости

```powershell
pip install -r requirements.txt
playwright install
```

---

## Запуск тестов

### Все тесты (Chromium, headless)

```powershell
pytest
```

### Конкретный браузер

```powershell
pytest --browser chromium
pytest --browser firefox
pytest --browser webkit
```

### Все браузеры сразу

```powershell
pytest --browser chromium --browser firefox --browser webkit
```

### Headed (с GUI браузером)

```powershell
pytest --headed --browser chromium
```

### Конкретный файл / тест

```powershell
pytest tests/test_auth.py
pytest tests/test_auth.py::test_auth_001_standard_user_login
```

### По маркеру

```powershell
pytest -m smoke
pytest -m "not performance"
```

### Замедленный режим (для отладки)

```powershell
pytest --headed --slowmo 500
```

---

## Отчёты

### HTML-отчёт (pytest-html)

```powershell
pytest --html=output/reports/report.html --self-contained-html
```

### Allure-отчёт

```powershell
pytest --alluredir=output/reports/allure
allure serve output/reports/allure
```

---

## Группы тестов

| Файл                    | ID тест-кейсов     | Кол-во | Описание                          |
|-------------------------|--------------------|--------|-----------------------------------|
| `test_auth.py`          | TC_AUTH_001–010    | 10+    | Авторизация                       |
| `test_inventory.py`     | TC_INV_001–010     | 10     | Страница товаров                  |
| `test_cart.py`          | TC_CART_001–010    | 10     | Корзина                           |
| `test_checkout.py`      | TC_CHECK_001–010   | 10     | Чекаут (2 шага)                   |
| `test_e2e.py`           | E2E                | 2      | Полный цикл покупки               |
| `test_ui.py`            | TC_UI_001–010      | 10     | Навигация и UI                    |
| `test_performance.py`   | TC_PERF_001–005    | 5+     | Производительность                |
| `test_cross_browser.py` | TC_XB_001–005      | 5+     | Кросс-браузер / разрешения        |

---

## Тестовые пользователи

| Ключ               | Username                   | Особенности                        |
|--------------------|----------------------------|------------------------------------|
| standard           | standard_user              | Всё работает нормально             |
| problem            | problem_user               | Баги в UI                          |
| performance_glitch | performance_glitch_user    | Искусственные задержки             |
| error              | error_user                 | Некоторые действия вызывают ошибки |
| visual             | visual_user                | Визуальные отличия                 |
| locked             | locked_out_user            | Заблокирован (вход запрещён)       |

Пароль для всех: `secret_sauce`

---

## Артефакты при падении тестов

- **Скриншоты** → `output/screenshots/FAIL__<test_name>.png`
- **Видео** → `output/videos/`
- **Отчёты** → `output/reports/`

---

## Технологии

- [Playwright](https://playwright.dev/python/) — браузерная автоматизация
- [pytest](https://pytest.org/) — тест-фреймворк
- [pytest-playwright](https://github.com/microsoft/playwright-pytest) — интеграция Playwright + pytest
- [Allure](https://allurereport.org/) — расширенные отчёты
- [pytest-html](https://pytest-html.readthedocs.io/) — HTML-отчёты
