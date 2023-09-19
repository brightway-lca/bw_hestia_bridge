from typing import Literal, Optional

import requests

import bw_hestia_bridge as bhb


stable_url = "https://api.hestia.earth"
staging_url = "https://api-staging.hestia.earth"


hestia_session = requests.Session()
hestia_session.headers.update({"Content-Type": "application/json"})


def _hestia_request(
    endpoint: str,
    query: Optional[dict] = None,
    req_type: Literal["get", "post"] = "get",
) -> dict:
    """Return the data necessary to query the Hestia API"""
    config = bhb.get_config()

    url = staging_url if config["use_staging"] else stable_url

    proxies = {
        "http": config["http_proxy"],
        "https": config["https_proxy"],
    }

    hestia_session.proxies.update(proxies)

    if req_type == "get":
        return hestia_session.get(f"{url}/{endpoint}", json=query).json()

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
