import re
from typing import Any, Literal, Optional, Union

import requests

from .base_api import base_api_data, nested_elements, valid_types


def search_hestia(
    query: Union[str, dict[str, str]],
    node_type: Optional[str] = None,
    fields: Optional[list[str]] = None,
    limit: Optional[int] = 10,
    how: Literal["or", "and", "exact"] = "or",
) -> list[dict[str, str]]:
    """
    Search the Hestia database.

    Parameters
    ----------
    query : str or dict
        A string to match to names in the Hestia database, or a dict of the
        form ``{"field_name": value}`` to match `field_name` instead of
        "name". See the examples below to see how to make more complex
        quieries.
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
    how : {"or", "and", "exact"}, optional (default: "or")
        Whether the search tries to match any word in `query` ("or"), all
        words in `query` ("and") or to match the whole query exactly
        ("exact").

    Returns
    -------
    A list of dicts containing the `fields` entries. Additionally, a "_score"
    value is returned, indicating the accuracy of the match found in the 
    Hestia database (results are sorted by decreasing "_score").

    Examples
    --------
    One can refine the query by searching for nodes that have a product with a
    name matching "Saplings" by using ::

        search_hestia({"products.term.name": "Saplings"})

    It is also possible to do multi-criteria searches as follow ::

        search_hestia({"name": "Ouidah", "products.term.name": "Saplings"})
    """
    url, proxies, headers = base_api_data()

    fields = fields or ["@type", "name", "@id"]

    how = how or "or"

    matches: list[dict] = []

    if not isinstance(query, dict):
        query = {"name": query}

    # check the query
    r = r"^(?P<path>\w+)\..+"

    for k, v in query.items():
        re_match = re.search(r, k)

        qk = {}

        if how in ("and", "or"):
            qk[k] = {"query": v, "operator": how}
        elif how == "exact":
            qk[f"{k}.keyword"] = v
        else:
            raise ValueError(f"Invalid `how` argument: '{how}'.")

        if re_match:
            path = re_match.groupdict()["path"]

            if path in nested_elements:
                is_nested = True

                matches.append({"nested": {"path": path, "query": {"match": qk}}})
            else:
                matches.append({"match": qk})
        else:
            matches.append({"match": qk})

    if node_type:
        assert (
            node_type.lower() in valid_types
        ), f"Valid `node_type` entries are {valid_types}"

        matches.append({"match": {"@type": node_type[0].upper() + node_type[1:]}})

    q: dict[str, Any] = {
        "fields": fields,
        "limit": limit,
        "query": {"bool": {"must": matches}},
    }

    res = requests.post(
        f"{url}/search", json=q, headers=headers, proxies=proxies
    ).json()

    return res.get("results", [])


def get_hestia_node(
    node_id: Union[str, dict[str, str]],
    node_type: Optional[str] = None,
    data_state: Optional[str] = None,
) -> dict:
    """
    Download the Hestia node associated to `node`.

    Parameters
    ----------
    node_id : str or dict[str, str]
        Hestia ID for the node or dictionary describing the node (e.g. returned from
        :func:`search_hestia`). If it's a dict, it must contain at least an "@type"
        and an "@id" entry.
    node_type : str, optional (default: taken from `node_id` or "cycle")
        A valid type among "actor", "animal", "bibliography", "completeness",
        "cycle", "emission", "impactassessment", "indicator",
        "infrastructure", "input", "management", "measurement",
        "organisation", "practice", "product", "property", "site", "source",
        "term", "transformation", or "transport". If not provided, will either
        be taken from `node_id` if it is a dict, or default to "cycle".
    data_state : str, optional (default: "recalculated")
        Version of the data, by default, use "recalculated" to download the
        more detailed version of the data. Use "original" to get the raw data.

    Returns
    -------
    The dict associated to the JSON-LD entry describing `node` in the
    Hestia database.
    """
    if isinstance(node_id, dict):
        assert "@type" in node_id, "`node` must contain an '@type' entry."
        assert "@id" in node_id, "`node` must contain an '@id' entry."

        node_type = node_id["@type"]
        node_id = node_id["@id"]
    else:
        node_type = node_type or "cycle"

    node_type = node_type.lower()

    url, proxies, headers = base_api_data()

    data_state = data_state or "recalculated"

    req_url = f"{url}/{node_type}s/{node_id}?dataState={data_state}"

    return requests.get(req_url, headers=headers, proxies=proxies).json()
