from functools import partial
from typing import Literal, Optional

from bw2io.importers.base_lci import LCIImporter
from bw2io.strategies import add_database_name, normalize_units

from . import set_config
from .hestia_api import get_hestia_node
from .strategies import (
    add_code_from_hestia_attributes,
    convert,
    drop_zeros,
    link_ecoinvent_biosphere,
    link_ecoinvent_technosphere,
)


class HestiaImporter(LCIImporter):
    def __init__(
        self,
        cycle_id: str,
        ecoinvent_label: str,
        data_state: Literal["original", "recalculated"] = "recalculated",
        staging: Optional[bool] = False,
        biosphere_label: Optional[str] = "biosphere3",
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
        staging : bool, optional (default: False)
            Whether to fetch the cycle from the staging Hestia API.
        """
        # move to staging if necessary
        set_config("use_staging", staging)

        # initialize variables
        self.db_name = f"Hestia cycle {cycle_id}"

        self.cycle_id = cycle_id

        self.data = get_hestia_node(
            node_id=cycle_id, node_type="cycle", data_state=data_state
        )

        self.strategies = [
            convert,
            normalize_units,
            drop_zeros,
            add_code_from_hestia_attributes,
            partial(add_database_name, name=self.db_name),
            partial(link_ecoinvent_biosphere, biosphere_label=biosphere_label),
            partial(
                link_ecoinvent_technosphere, ecoinvent_database_label=ecoinvent_label
            ),
        ]
