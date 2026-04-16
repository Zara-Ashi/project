from playwright.sync_api import Page
from pages.base_page import BasePage


class CompletePage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.complete_header  = page.locator(".complete-header")
        self.complete_text    = page.locator(".complete-text")
        self.back_home_button = page.locator("[data-test='back-to-products']")
        self.pony_image       = page.locator(".pony_express")

    def is_complete_header_visible(self) -> bool:
        return self.complete_header.is_visible()

    def get_header_text(self) -> str:
        return self.complete_header.inner_text()

    def get_complete_text(self) -> str:
        return self.complete_text.inner_text()

    def go_back_home(self):
        self.back_home_button.click()

    def is_success_image_visible(self) -> bool:
        return self.pony_image.is_visible()
