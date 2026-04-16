USERS = {
    "standard":          {"username": "standard_user",          "password": "secret_sauce"},
    "locked":            {"username": "locked_out_user",         "password": "secret_sauce"},
    "problem":           {"username": "problem_user",            "password": "secret_sauce"},
    "performance_glitch":{"username": "performance_glitch_user", "password": "secret_sauce"},
    "error":             {"username": "error_user",              "password": "secret_sauce"},
    "visual":            {"username": "visual_user",             "password": "secret_sauce"},
}

INVALID_USERS = {
    "wrong_password":  {"username": "standard_user", "password": "wrong_pass"},
    "fake_user":       {"username": "fake_user",     "password": "secret_sauce"},
    "empty_username":  {"username": "",              "password": "secret_sauce"},
    "empty_password":  {"username": "standard_user", "password": ""},
    "sql_injection":   {"username": "' OR '1'='1",  "password": "anything"},
    "xss":             {"username": "<script>alert(1)</script>", "password": "test"},
}

ERROR_MESSAGES = {
    "wrong_credentials": "Epic sadface: Username and password do not match any user in this service",
    "username_required": "Epic sadface: Username is required",
    "password_required": "Epic sadface: Password is required",
    "locked_out":        "Epic sadface: Sorry, this user has been locked out.",
}
