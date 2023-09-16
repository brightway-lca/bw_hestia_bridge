from ..utils.config import _config


def base_api_data() -> tuple[str, str, dict, dict]:
    """Return the data necessary to query the Hestia API"""
    url = _config["hestia_api"].strip("/")

    token = _config["hestia_token"]

    proxies = {
        "http": _config["http_proxy"],
        "https": _config["https_proxy"],
    }

    headers = {"Content-Type": "application/json", "X-ACCESS-TOKEN": token}

    return url, token, proxies, headers
