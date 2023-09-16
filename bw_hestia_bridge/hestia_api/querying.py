import re
from typing import Optional, Union

import requests

from .base_data import base_api_data

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


def search_hestia(
    query: Union[str, dict[str, str]],
    node_type: Optional[str] = None,
    fields: Optional[list[str]] = None,
    limit: Optional[int] = 10,
) -> list[dict[str, str]]:
    """
    Search the Hestia database.

    Parameters
    ----------
    query : str or dict
        A string to match to names in the Hestia database, or a dict of the
        form ``{"field_name": value}`` to match `field_name` instead of
        "name". One can also refine this by searching for nodes that have a
        product with a name matching "Saplings" by using
        ``{"products.term.name": "Saplings"}``.
    node_type : str, optional (default: any type)
        A valid type among "actor", "animal", "bibliography", "completeness",
        "cycle", "emission", "impactassessment", "indicator",
        "infrastructure", "input", "management", "measurement",
        "organisation", "practice", "product", "property", "site", "source",
        "term", "transformation", or "transport".
    fields : list[str], optional (default: ["@type", "name", "@id"])
        Fields that will be returned in the search results.
    limit : int, optional (default: 10)

    Returns
    -------
    A list of dicts containing the `fields` entries.
    """
    url, token, proxies, headers = base_api_data()

    fields = fields or ["@type", "name", "@id"]

    matches = []

    if not isinstance(query, dict):
        matches.append({"match": {"name": query}})
    else:
        r = r"(?P<path>\w+)\..+"
        key = next(iter(query))

        re_match = re.search(r, key)

        if re_match:
            path = re_match.groupdict()["path"]

            matches.append({"nested": {"path": path, "query": {"match": query}}})
        else:
            matches.append({"match": query})

    if node_type:
        assert (
            node_type.lower() in valid_types
        ), f"Valid `node_type` entries are {valid_types}"

        matches.append({"match": {"@type": node_type[0].upper() + node_type[1:]}})

    q = {"query": {"bool": {"must": matches}}, "fields": fields, "limit": limit}

    return requests.post(
        f"{url}/search", json=q, headers=headers, proxies=proxies
    ).json()["results"]


def get_hestia_node(node: dict[str, str], data_state: Optional[str] = None) -> dict:
    """
    Download the Hestia node associated to `node`.

    Parameters
    ----------
    node : dict[str, str]
         Dictionary describing the node. It must contain at least an "@type"
        and an "@id" entry.
    data_state : str, optional (default: "recalculated")
        Version of the data, by default, use "recalculated" to download the
        more detailed version of the data. Use "original" to get the raw data.

    Returns
    -------
    The dict associated to the JSON-LD entry describing `node` in the
    Hestia database.
    """
    assert "@type" in node, "`node` must contain an '@type' entry."
    assert "@id" in node, "`node` must contain an '@id' entry."

    url, token, proxies, headers = base_api_data()

    ntype = node["@type"].lower()
    nid = node["@id"]

    data_state = data_state or "recalculated"

    req_url = f"{url}/{ntype}s/{nid}?dataState={data_state}"

    return requests.get(req_url, headers=headers, proxies=proxies).json()


def simple_hestia(
    node_type: str,
    node_id: str,
    staging: Optional[bool] = False,
    recalculated: Optional[bool] = False,
):
    """
    Download the Hestia node type `node_type` with id `node_id`

    Parameters
    ----------
    node_type: str. One of `valid_types`.
    node_id: str.
    staging: bool. Use staging API URL.
    recalculated: bool. Use recalculated data, only `node_type` `cycle`.

    Returns
    -------
    JSON-LD dictionary
    """
    if node_type not in valid_types:
        raise ValueError(f"Invalid type {node_type}")

    url_base = (
        "https://api-staging.hestia.earth" if staging else "https://api.hestia.earth"
    )
    headers = {"Content-Type": "application/json"}
    url = f"{url_base}/{node_type}s/{node_id}"

    if node_type == "cycle":
        if recalculated:
            params = {"dataState": "recalculated"}
        else:
            params = {"dataState": "original"}
    else:
        params = {}

    return requests.get(url, params=params, headers=headers).json()
