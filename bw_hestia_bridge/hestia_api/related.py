from typing import Literal, Optional, Union

import requests

from .base_api import base_api_data, nested_elements, valid_types
from .querying import search_hestia, get_node_type


def term_related_cycles(
    node_id: str,
    term_type: Optional[str] = None,
    direction: Literal["inputs", "products", "both"] = "both",
) -> list[dict]:
    '''
    Return all related cycles from a given term.

    Parameters
    ----------
    node_id : str
        The ID of the node in Hestia.
    term_type : str, optional (default: autodetected)
        Type of the term (transport, emission...)
    direction : str, optional (default: both)
        Direction of the relation (is the term in the inputs
        or in the products of the cycle).
    '''
    url, proxies, headers = base_api_data()

    term_type = term_type or search_hestia(
        {"@id": node_id}, how="exact", fields=["termType"]
    )[0].get("termType", "")

    q: dict[str, Union[int, str]] = {"limit": 10000}

    if direction != "both" and term_type:
        q["relationship"] = f"{direction}{term_type}"

    res = requests.get(
        f"{url}/terms/{node_id}/cycles", params=q, headers=headers,
        proxies=proxies
    ).json()

    return res.get("results", [])
