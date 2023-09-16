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
    name: Union[str, dict[str, str]],
    node_type: Optional[str] = None,
    fields: Optional[list[str]] = None,
    limit: Optional[int] = 10
) -> list[dict[str, str]]:
    '''
    Search the Hestia database.

    Parameters
    ----------
    name : str or dict
        A string to match to the names of the Hestia database, or a
        dict of the form ``{"field_name": value}`` to search `field_name`
        instead of "name". One can also refine this by searching for
        nodes that have a product with a name matching "sapling" by
        using ``{"products.term.name": "sapling"}``.
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
    '''
    url, token, proxies, headers = base_api_data()

    fields = fields or ["@type", "name", "@id"]

    matches = []

    if not isinstance(name, dict):
        matches.append({"match": {"name": name}})
    else:
        r = r"(?P<path>\w+)\..+"
        key = next(iter(name))

        re_match = re.search(r, key)

        if re_match:
            path = re_match.groupdict()["path"]

            matches.append({
                'nested':{
                    'path': path,
                    'query': {'match': name}
                }
            })
        else:
            matches.append({'match': name})

    if node_type:
        assert node_type.lower() in valid_types, \
            f"Valid `node_type` entries are {valid_types}"

        matches.append(
            {"match": {"@type": node_type[0].upper() + node_type[1:]}})

    query = {
        "query": {"bool": {"must": matches}},
        "fields": fields,
        "limit": limit
    }

    return requests.post(
        f"{url}/search", json=query, headers=headers, proxies=proxies
    ).json()["results"]


def get_hestia_node(
    node: dict[str, str],
    data_state: Optional[str] = None
) -> dict:
    '''
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
    '''
    assert "@type" in node, "`node` must contain an '@type' entry."
    assert "@id" in node, "`node` must contain an '@id' entry."

    url, token, proxies, headers = base_api_data()

    ntype = node["@type"].lower()
    nid = node["@id"]

    data_state = data_state or "recalculated"

    req_url = f"{url}/{ntype}s/{nid}?dataState={data_state}"

    return requests.get(req_url, headers=headers, proxies=proxies).json()

