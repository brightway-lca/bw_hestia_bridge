from functools import partial
from typing import Optional

from bw2io.importers.base_lci import LCIImporter
from bw2io.strategies import add_database_name, normalize_units

from . import set_config
from .hestia_api import get_hestia_node
from .strategies import add_code_from_hestia_attributes, convert


class HestiaImporter(LCIImporter):
    def __init__(
        self,
        cycle_id: str,
        data_state: Optional[str] = "recalculated",
        staging: Optional[bool] = False,
    ) -> None:
        set_config("use_staging", staging)
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
