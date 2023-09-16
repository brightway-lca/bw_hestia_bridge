import bw_hestia_bridge as bhb


def base_api_data() -> tuple[str, str, dict, dict]:
    ''' Return the data necessary to query the Hestia API '''
    url = bhb._config["hestia_api"].strip("/")

    token = bhb._config["hestia_token"]

    proxies = {
        "http": bhb._config["http_proxy"],
        "https": bhb._config["https_proxy"],
    }

    headers = {'Content-Type': 'application/json', 'X-ACCESS-TOKEN': token}

    return url, token, proxies, headers
