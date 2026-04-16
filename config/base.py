BASE_URL = "https://www.saucedemo.com"

TIMEOUTS = {
    "default": 10000,
    "navigation": 30000,
    "slow_network": 60000,
}

PERFORMANCE = {
    "page_load_threshold_ms": 3000,
    "button_response_ms": 1000,
}

VIEWPORTS = {
    "desktop_fhd": {"width": 1920, "height": 1080},
    "desktop_hd":  {"width": 1366, "height": 768},
    "mobile":      {"width": 375,  "height": 667},
}
