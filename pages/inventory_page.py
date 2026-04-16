from playwright.sync_api import Page
from pages.base_page import BasePage


class InventoryPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.title           = page.locator(".title")
        self.items           = page.locator(".inventory_item")
        self.item_names      = page.locator(".inventory_item_name")
        self.item_prices     = page.locator(".inventory_item_price")
        self.item_images     = page.locator(".inventory_item img")
        self.sort_dropdown   = page.locator("[data-test='product-sort-container']")
        self.cart_badge      = page.locator(".shopping_cart_badge")
        self.cart_icon       = page.locator(".shopping_cart_link")
        self.burger_menu     = page.locator("#react-burger-menu-btn")
        self.burger_close    = page.locator("#react-burger-cross-btn")
        self.menu_logout     = page.locator("#logout_sidebar_link")
        self.menu_reset      = page.locator("#reset_sidebar_link")
        self.menu_all_items  = page.locator("#inventory_sidebar_link")

    def open(self):
        self.navigate("/inventory.html")
        self.wait_for_load()

    def get_item_count(self) -> int:
        return self.items.count()

    def get_all_names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def get_all_prices(self) -> list[float]:
        raw = self.item_prices.all_inner_texts()
        return [float(p.replace("$", "")) for p in raw]

    def add_to_cart_by_name(self, name: str):
        item = self.page.locator(".inventory_item").filter(has_text=name)
        item.locator("button").click()

    def remove_from_cart_by_name(self, name: str):
        item = self.page.locator(".inventory_item").filter(has_text=name)
        item.locator("button").click()

    def get_button_text_by_name(self, name: str) -> str:
        item = self.page.locator(".inventory_item").filter(has_text=name)
        return item.locator("button").inner_text()

    def get_cart_badge_count(self) -> int:
        if self.cart_badge.is_visible():
            return int(self.cart_badge.inner_text())
        return 0

    def sort_by(self, option: str):
        """Options: 'az', 'za', 'lohi', 'hilo'"""
        self.sort_dropdown.select_option(option)

    def go_to_cart(self):
        self.cart_icon.click()

    def open_burger_menu(self):
        self.burger_menu.click()
        self.page.wait_for_selector("#logout_sidebar_link", state="visible")

    def logout(self):
        self.open_burger_menu()
        self.menu_logout.click()

    def click_item_image(self, index: int = 0):
        self.item_images.nth(index).click()

    def get_image_natural_width(self, index: int) -> int:
        img = self.item_images.nth(index)
        return img.evaluate("el => el.naturalWidth")
