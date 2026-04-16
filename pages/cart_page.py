from playwright.sync_api import Page
from pages.base_page import BasePage


class CartPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.cart_items         = page.locator(".cart_item")
        self.item_names         = page.locator(".inventory_item_name")
        self.item_prices        = page.locator(".inventory_item_price")
        self.item_quantities    = page.locator(".cart_quantity")
        self.checkout_button    = page.locator("[data-test='checkout']")
        self.continue_shopping  = page.locator("[data-test='continue-shopping']")
        self.empty_message      = page.locator(".cart_list")

    def open(self):
        self.navigate("/cart.html")
        self.wait_for_load()

    def get_item_count(self) -> int:
        return self.cart_items.count()

    def get_item_names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def get_item_prices(self) -> list[float]:
        raw = self.item_prices.all_inner_texts()
        return [float(p.replace("$", "")) for p in raw]

    def remove_item_by_name(self, name: str):
        item = self.page.locator(".cart_item").filter(has_text=name)
        item.locator("button").click()

    def proceed_to_checkout(self):
        self.checkout_button.click()

    def continue_shopping_click(self):
        self.continue_shopping.click()

    def is_empty(self) -> bool:
        return self.cart_items.count() == 0
