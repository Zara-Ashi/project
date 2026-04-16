EXPECTED_PRODUCTS = [
    {"name": "Sauce Labs Backpack",            "price": 29.99},
    {"name": "Sauce Labs Bike Light",          "price": 9.99},
    {"name": "Sauce Labs Bolt T-Shirt",        "price": 15.99},
    {"name": "Sauce Labs Fleece Jacket",       "price": 49.99},
    {"name": "Sauce Labs Onesie",              "price": 7.99},
    {"name": "Test.allTheThings() T-Shirt (Red)", "price": 15.99},
]

EXPECTED_NAMES = [p["name"] for p in EXPECTED_PRODUCTS]
EXPECTED_PRICES = [p["price"] for p in EXPECTED_PRODUCTS]

TAX_RATE = 0.08  # ~8%

CHECKOUT_INFO = {
    "first_name": "Test",
    "last_name":  "User",
    "postal_code": "12345",
}
