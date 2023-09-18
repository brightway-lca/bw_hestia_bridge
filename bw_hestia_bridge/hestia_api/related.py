from typing import Literal, Optional, Union

import requests

from .base_api import base_api_data, nested_elements, valid_types
from .querying import search_hestia, gest_hestia, get_node_type


def cycle_related_cycles(cycle_id: str) -> list[dict]:
    '''
    Get all the cycles that are in the connected graph of `cycle_id`.

    Parameters
    ----------
    cycle_id : str
        Hestia ID of the initial cycle.

    Returns
    -------
    List of cycles of the form: ::

        [
            {
                "from": {@type="Cycle", @id: PARENT_CYCLE_ID},
                "to": {@type: "Cycle", @id: CHILD_CYCLE_ID},
                "via": {@type: "Term", @id: PRODUCT_TERM_ID}
            },
            ...
        ]
    '''
    url, proxies, headers = base_api_data()

    q: dict[str, Union[int, str]] = {
        "limit": 10000,
        "connections" : "ImpactAssessmentcycle,CycleinputsimpactAssessment",
        "includeAggregated": True
    }

    res = requests.get(
        f"{url}/cycles/{cycle_id}/deep-relations", params=q, headers=headers,
        proxies=proxies
    ).json()

    # make the list of cycles
    cycle_list: list[dict] = []

    for elt in res:
        eid = elt["@id"]
        etype = elt["@type"]

        if etype == "Cycle":
            for cid in elt["parentIds"]:
                parent = get_hestia_node(cid, "ImpactAssessment")

                product = parent["product"]

                # the "cycle" entry in impact assessment is its parent
                grandparent = parent["cycle"]

                cycle_list.append({
                    "from": {"@id": grandparent, "@type": "Cycle"},
                    "to": {"@id": eid, "@type": "Cycle"},
                    "via": product
                })

    return cycle_list


def term_connected_cycles(
    node_id: str,
    term_type: Optional[str] = None,
    direction: Literal["inputs", "products", "both"] = "both",
) -> list[dict]:
    '''
    Return all cycles directly connected to a given term.

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
