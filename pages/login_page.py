from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.username_input  = page.locator("#user-name")
        self.password_input  = page.locator("#password")
        self.login_button    = page.locator("#login-button")
        self.error_message   = page.locator("[data-test='error']")
        self.error_button    = page.locator(".error-button")

    def open(self):
        self.navigate("/")
        self.wait_for_load()

    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def get_error_message(self) -> str:
        return self.error_message.inner_text()

    def is_error_visible(self) -> bool:
        return self.error_message.is_visible()

    def clear_error(self):
        self.error_button.click()

    def get_username_value(self) -> str:
        return self.username_input.input_value()
