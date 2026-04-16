from playwright.sync_api import Page
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        # Step 1
        self.first_name_input = page.locator("[data-test='firstName']")
        self.last_name_input  = page.locator("[data-test='lastName']")
        self.postal_input     = page.locator("[data-test='postalCode']")
        self.continue_button  = page.locator("[data-test='continue']")
        self.cancel_button    = page.locator("[data-test='cancel']")
        self.error_message    = page.locator("[data-test='error']")
        # Step 2
        self.finish_button    = page.locator("[data-test='finish']")
        self.item_total_label = page.locator(".summary_subtotal_label")
        self.tax_label        = page.locator(".summary_tax_label")
        self.total_label      = page.locator(".summary_total_label")
        self.summary_items    = page.locator(".cart_item")

    def open_step1(self):
        self.navigate("/checkout-step-one.html")
        self.wait_for_load()

    def fill_info(self, first_name: str, last_name: str, postal_code: str):
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.postal_input.fill(postal_code)

    def click_continue(self):
        self.continue_button.click()

    def click_cancel(self):
        self.cancel_button.click()

    def click_finish(self):
        self.finish_button.click()

    def get_error_message(self) -> str:
        return self.error_message.inner_text()

    def is_error_visible(self) -> bool:
        return self.error_message.is_visible()

    def get_item_total(self) -> float:
        text = self.item_total_label.inner_text()
        return float(text.split("$")[-1])

    def get_tax(self) -> float:
        text = self.tax_label.inner_text()
        return float(text.split("$")[-1])

    def get_total(self) -> float:
        text = self.total_label.inner_text()
        return float(text.split("$")[-1])

    def get_summary_item_count(self) -> int:
        return self.summary_items.count()
