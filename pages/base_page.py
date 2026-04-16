from playwright.sync_api import Page
from config.base import BASE_URL, TIMEOUTS


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = BASE_URL

    def navigate(self, path: str = ""):
        self.page.goto(f"{self.base_url}/{path.lstrip('/')}")

    def get_url(self) -> str:
        return self.page.url

    def wait_for_load(self):
        self.page.wait_for_load_state("networkidle", timeout=TIMEOUTS["navigation"])

    def take_screenshot(self, name: str):
        self.page.screenshot(path=f"output/screenshots/{name}.png")

    def get_title(self) -> str:
        return self.page.title()
