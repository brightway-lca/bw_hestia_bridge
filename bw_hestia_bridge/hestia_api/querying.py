import re
from typing import Any, Optional, Union

import requests

from .base_data import base_api_data


def search_hestia(
    query: Union[str, dict[str, str]],
    node_type: Optional[str] = None,
    fields: Optional[list[str]] = None,
    limit: Optional[int] = 10,
    match_all_words: bool = False
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
        The maximum number of results that will be returned (best match come
        first).
    match_all_words : bool, optional (default: False)
        Whether the search tries to match all words in the `query` string.
        Set to True for more precise results.

    Returns
    -------
    A list of dicts containing the `fields` entries.
    """
    url, token, proxies, headers = base_api_data()

    fields = fields or ["@type", "name", "@id"]

    matches: list[dict] = []

    if not isinstance(query, dict):
        if match_all_words:
            matches.append({
                "match": {"name": {"query": query, "operator": "and"}}
            })
        else:
            matches.append({"match": {"name": query}})
    else:
        r = r"^(?P<path>\w+)\..+"

        for k, v in query.items():
            re_match = re.search(r, k)

            if re_match:
                path = re_match.groupdict()["path"]

                if path in nested_elements:
                    is_nested = True

                    matches.append({
                        "nested": {"path": path, "query": {"match": {k: v}}}
                    })
                else:
                    matches.append({'match': {k: v}})
            elif match_all_words:
                matches.append({
                    'match': {k: {"query": v, "operator": "and"}}
                })
            else:
                matches.append({'match': {k: v}})

    if node_type:
        assert (
            node_type.lower() in valid_types
        ), f"Valid `node_type` entries are {valid_types}"

        matches.append({"match": {"@type": node_type[0].upper() + node_type[1:]}})

    q: dict[str, Any] = {
        "fields": fields,
        "limit": limit,
        "query": {"bool": {"must": matches}}
    }

    res = requests.post(
        f"{url}/search", json=q, headers=headers, proxies=proxies
    ).json()

    return res.get("results", [])


def get_hestia_node(
    node: dict[str, str],
    data_state: Optional[str] = None
) -> dict:
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
    'inputs',
    'practices',
    'otherSites',
    'animals',
    'products',
    'transformations',
    'emissions',
    'emissionsResourceUse',
    'impacts',
    'endpoints',
    'measurements',
    'management',
    'metaAnalyses',
    'subClassOf',
    'defaultProperties'
}
