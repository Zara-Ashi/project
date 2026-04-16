import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from config.base import BASE_URL, TIMEOUTS
from config.users import USERS
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.complete_page import CompletePage


@pytest.fixture(scope="session")
def browser_type_launch_args():
    return {"headless": True, "slow_mo": 0}


@pytest.fixture
def context(browser: Browser):
    ctx = browser.new_context(
        record_video_dir="output/videos/",
        viewport={"width": 1280, "height": 720},
    )
    ctx.set_default_timeout(TIMEOUTS["default"])
    yield ctx
    ctx.close()


@pytest.fixture
def page(context: BrowserContext) -> Page:
    p = context.new_page()
    yield p
    p.close()


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    lp = LoginPage(page)
    lp.open()
    return lp


@pytest.fixture
def logged_in_page(page: Page) -> Page:
    """Returns pages already logged in as standard_user."""
    lp = LoginPage(page)
    lp.open()
    lp.login(USERS["standard"]["username"], USERS["standard"]["password"])
    page.wait_for_url("**/inventory.html")
    return page

@pytest.fixture
def inventory_page(logged_in_page: Page) -> InventoryPage:
    return InventoryPage(logged_in_page)


@pytest.fixture
def cart_page(logged_in_page: Page) -> CartPage:
    return CartPage(logged_in_page)


@pytest.fixture
def checkout_page(logged_in_page: Page) -> CheckoutPage:
    return CheckoutPage(logged_in_page)


@pytest.fixture
def complete_page(logged_in_page: Page) -> CompletePage:
    return CompletePage(logged_in_page)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        page: Page = item.funcargs.get("pages") or item.funcargs.get("logged_in_page")
        if page:
            safe_name = item.nodeid.replace("/", "_").replace("::", "__")
            page.screenshot(path=f"output/screenshots/FAIL__{safe_name}.png")
