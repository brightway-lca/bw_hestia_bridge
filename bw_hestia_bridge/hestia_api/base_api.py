from typing import Literal, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import bw_hestia_bridge as bhb


stable_url = "https://api.hestia.earth"
staging_url = "https://api-staging.hestia.earth"


# create session for Hestia calls
hestia_session = requests.Session()
hestia_session.headers.update({"Content-Type": "application/json"})

retries = 3

retry = Retry(
    total=retries,
    read=retries,
    connect=retries,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
)

adapter = HTTPAdapter(max_retries=retry)
hestia_session.mount('http://', adapter)
hestia_session.mount('https://', adapter)


# make the request

def _hestia_request(
    endpoint: str,
    query: Optional[dict] = None,
    req_type: Literal["get", "post"] = "get",
) -> dict:
    """
    Query the Hestia API.

    Parameters
    ----------
    endpoint : str
        The API endpoint (e.g. "search").
    query : dict, optional (default: None)
        Additional queries (passed via something like "?q1=v1&q2=v2").
    req_type : str, "get" or "post"
        The type of request that will be performed.
    """
    config = bhb.get_config()

    url = staging_url if config["use_staging"] else stable_url

    proxies = {
        "http": config["http_proxy"],
        "https": config["https_proxy"],
    }

    hestia_session.proxies.update(proxies)

    if req_type == "get":
        return hestia_session.get(f"{url}/{endpoint}", params=query).json()

    return hestia_session.post(f"{url}/{endpoint}", json=query).json()


# Hestia database information

valid_types = {
    "actor",
    "animal",
    "bibliography",
    "completeness",
    "cycle",
    "emission",
    "impactassessment",
    "indicator",
    "infrastructure",
    "input",
    "management",
    "measurement",
    "organisation",
    "practice",
    "product",
    "property",
    "site",
    "source",
    "term",
    "transformation",
    "transport",
}

nested_elements = {
    "inputs",
    "practices",
    "otherSites",
    "animals",
    "products",
    "transformations",
    "emissions",
    "emissionsResourceUse",
    "impacts",
    "endpoints",
    "measurements",
    "management",
    "metaAnalyses",
    "subClassOf",
    "defaultProperties",
}
