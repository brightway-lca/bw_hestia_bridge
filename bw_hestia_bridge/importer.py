from functools import partial
from typing import Literal, Optional

from bw2io.importers.base_lci import LCIImporter
from bw2io.strategies import add_database_name, normalize_units

from . import get_config, set_config
from .hestia_api import get_hestia_node
from .strategies import add_code_from_hestia_attributes, convert


class HestiaImporter(LCIImporter):
    def __init__(
        self,
        cycle_id: str,
        data_state: Literal["original", "recalculated"] = "recalculated",
        staging: Optional[bool] = False,
    ) -> None:
        '''
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
        '''
        # move to staging if necessary
        old_staging = get_config("use_staging")
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
            add_code_from_hestia_attributes,
            partial(add_database_name, name=self.db_name),
        ]

        # revert config to initial value
        set_config("use_staging", old_staging)
