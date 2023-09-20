from functools import partial
from typing import Literal, Optional

from bw2io.importers.base_lci import LCIImporter
from bw2io.strategies import add_database_name, normalize_units

from . import set_config
from .hestia_api import get_cycle_graph, get_hestia_node
from .strategies import (
    Converter,
    add_code_from_hestia_attributes,
    drop_zeros,
    link_ecoinvent_biosphere,
    link_ecoinvent_technosphere,
)


class HestiaImporter(LCIImporter):
    def __init__(
        self,
        cycle_id: str,
        ecoinvent_label: str,
        expand_graph: Optional[bool] = True,
        data_state: Literal["original", "recalculated"] = "recalculated",
        biosphere_label: Optional[str] = "biosphere3",
        staging: Optional[bool] = None,
    ) -> None:
        """
        Import a Hestia cycle as a Brightway database.

        Parameters
        ----------
        cycle_id : str
            The Hestia ID for the cycle.
        data_state : str, optional (default: recalculated)
            Whether to use recalculated data information from Hestia
            or the raw "original" data.
        staging : bool, optional (default: from configuration)
            Whether to fetch the cycle from the staging Hestia API.
        """
        # move to staging if necessary
        self._staging = staging
        self._convertor = Converter(staging)

        # initialize variables
        extended = " expanded" if expand_graph else ""
        self.db_name = f"Hestia cycle {cycle_id}{extended}"

        self.cycle_id = cycle_id

        self.data = self._convertor.convert(
            get_hestia_node(node_id=cycle_id, node_type="cycle", data_state=data_state,
                            staging=staging)
        )

        if expand_graph:
            self.get_suppliers(cycle_id=cycle_id, data_state=data_state)

        self.strategies = [
            normalize_units,
            drop_zeros,
            add_code_from_hestia_attributes,
            partial(add_database_name, name=self.db_name),
            partial(link_ecoinvent_biosphere, biosphere_label=biosphere_label),
            partial(
                link_ecoinvent_technosphere, ecoinvent_database_label=ecoinvent_label
            ),
        ]

    def get_suppliers(self, cycle_id: str, data_state: str) -> None:
        graph = get_cycle_graph(cycle_id, staging=self._staging)
        for element in graph:
            if "from" not in element or element["from"].get("@type") != "Cycle":
                continue
            nodes = self._convertor.convert(
                get_hestia_node(
                    node_id=element["from"]["@id"],
                    node_type="cycle",
                    data_state=data_state,
                    staging=self._staging,
                )
            )
            for new_ds in nodes:
                new_ds["graph_element"] = element
            self.data.extend(nodes)
