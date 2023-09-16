import requests

from typing import Optional

from .base_data import base_api_data


def search_hestia(
    name: str,
    fields: Optional[list[str]] = None,
    limit: Optional[int] = 10
) -> list[dict[str, str]]:
    '''
    Search the Hestia database.

    Parameters
    ----------
    name : str
        A string to match to the names of the Hestia database.
    fields : list[str], optional (default: ["@type", "name", "@id"])
        Fields that will be returned in the search results.
    limit : int, optional (default: 10)

    Returns
    -------
    A list of dicts containing the `fields` entries.
    '''
    url, token, proxies, headers = base_api_data()

    fields = fields or ["@type", "name", "@id"]

    query = {
        "query": {
            "bool": {
                "must": [
                    {"match": {"name": name}}
                ]
            }
        },
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

