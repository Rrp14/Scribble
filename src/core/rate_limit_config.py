RATE_LIMITS = {
    # AUTH (IP-based)
    "AUTH_LOGIN": {
        "limit": 5,
        "window": 60,
        "use_user": False,
    },
    "AUTH_REGISTER": {
        "limit": 3,
        "window": 60,
        "use_user": False,
    },
    "AUTH_REFRESH": {
        "limit": 10,
        "window": 60,
        "use_user": False,
    },

    # NOTES (USER-based)
    "NOTES_LIST": {
        "limit": 60,
        "window": 60,
        "use_user": True,
    },
    "NOTES_CREATE": {
        "limit": 20,
        "window": 60,
        "use_user": True,
    },
    "NOTES_UPDATE": {
        "limit": 20,
        "window": 60,
        "use_user": True,
    },
    "NOTES_DELETE": {
        "limit": 10,
        "window": 60,
        "use_user": True,
    },
}
