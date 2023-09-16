import requests

from typing import Optional

from .base_data import base_api_data


def search_hestia(
    name: str,
    fields: Optional[list[str]] = None
) -> list[dict[str, str]]:
    '''
    Search the Hestia database.

    Parameters
    ----------
    name : str
        A string to match to the names of the Hestia database.
    fields : list[str], optional (default: ["@type", "name", "@id"])
        Fields returned by the search.

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
    }

    return requests.post(
        f"{url}/search", json=query, headers=headers, proxies=proxies
    ).json()["results"]


def get_hestia_node(node: dict[str, str]) -> dict:
    '''
    Download the Hestia node associated to `node`.

    Parameters
    ----------
    node : dict[str, str]
         Dictionary describing the node. It must contain at least an "@type"
        and an "@id" entry.

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

    return requests.get(
        f"{url}/{ntype}s/{nid}", headers=headers, proxies=proxies).json()

