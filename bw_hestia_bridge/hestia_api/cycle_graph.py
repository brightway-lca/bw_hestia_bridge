from typing import Literal, Optional, Union

import requests

from ..utils import get_config
from .base_api import base_api_data
from .querying import search_hestia, get_hestia_node


def get_cycle_graph(cycle_id: str) -> list[dict]:
    """
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

    Raises
    ------
    ``ValueError`` if `cycle_id` is not found.
    '''
    """
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

    if not isinstance(res, list):
        api_type = "staging" if get_config("use_staging") else "stable"
        raise ValueError(f"{cycle_id} not found using the {api_type} API.")

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
