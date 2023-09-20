import warnings
from collections import defaultdict
from functools import lru_cache
from typing import Optional, Tuple, Union

from .. import get_config
from ..hestia_api import get_hestia_node
from ..utils import get_config


def transformation_to_str(val: Union[str, None]) -> int:
    if not val:
        return "0"
    else:
        return val


class Converter:

    """Convert Hestia data into a BW-compatible form"""

    def __init__(self, staging: Optional[bool] = None):
        self._staging = staging or get_config("use_staging")

    def convert(self, source: dict) -> list:
        return_data = []

        cycle_id = source["@id"]

        target = self.get_basic_metadata(source, cycle_id)
        self.add_practices(source=source, target=target)
        if "animals" in source:
            target["animals"] = source["animals"]

        target["exchanges"] = self.get_inputs(source, cycle_id, None)
        new_exchanges, new_datasets = self.get_products(source, cycle_id)
        target["exchanges"].extend(new_exchanges)
        return_data.extend(new_datasets)

        new_exchanges = self.get_emissions(source)
        target["exchanges"].extend(new_exchanges)

        new_datasets = self.get_transformations(source, cycle_id)
        return_data.extend(new_datasets)

        return_data.append(target)

        # TBD: Make sure we aren't adding duplicate product nodes
        return return_data

    def get_basic_metadata(self, obj: dict, cycle_id: str) -> dict:
        """
        Return a minimum subset of the object data, partly
        renamed to fit the BW format.
        """
        EXTRAS = {
            "createdAt",
            "updatedAt",
            "endDate",
            "cycleDuration",
            "functionalUnit",
            "defaultMethodClassification",
            "defaultMethodClassificationDescription",
        }

        site = self.get_site(obj["site"]["@id"])

        return {
            "@id": cycle_id,
            "comment": obj.get("description"),
            "name": obj["name"],
            "location": site["name"],
            "hestia_site_id": obj["site"]["@id"],
            "hestia_site": site,
            "type": "process",
            "extra_metadata": {key: obj[key] for key in EXTRAS if key in obj},
        }

    @lru_cache
    def get_site(self, node_id: str) -> str:
        location = get_hestia_node(
            node_type="site", node_id=node_id, staging=self._staging
        )

        if "name" not in location:
            warnings.warn(f"Can't find location {node_id}; using `GLO` instead")
            return "GLO"

        return location

    def _add_suffixed(
        self, source: dict, target: dict, label: str, fields: set, currency: bool
    ) -> None:
        if label in source:
            target[label] = {key: source[key] for key in fields if key in source}
            if "currency" in source and currency:
                target[label]["currency"] = source["currency"]

    def add_price(self, source: dict, target: dict) -> None:
        self._add_suffixed(source, target, "price", PRICE, True)

    def add_cost(self, source: dict, target: dict) -> None:
        self._add_suffixed(source, target, "cost", COST, True)

    def add_distance(self, source: dict, target: dict) -> None:
        self._add_suffixed(source, target, "distance", DISTANCE, False)

    def add_optional_fields(self, source: dict, target: dict) -> None:
        for field in OPTIONAL_FIELDS:
            if field in source:
                target[field] = source[field]
        for orig, new in MAPPED_OPTIONAL_FIELDS.items():
            if orig in source:
                target[new] = source[orig]

    def get_inputs(
        self, obj: dict, cycle_id: str, transformation_id: Optional[str]
    ) -> list:
        counter = defaultdict(int)

        exchange_list = []

        for inpt in obj["inputs"]:
            if "value" not in inpt:
                continue

            group = "{}-{}".format(inpt["term"]["name"], counter[inpt["term"]["name"]])
            counter[inpt["term"]["name"]] += 1

            exchange = {
                "name": inpt["term"]["name"],
                "cycle_id": cycle_id,
                "term_type": inpt["term"]["termType"],
                "term_id": inpt["term"]["@id"],
                "unit": inpt["term"].get("units"),
                "amount": inpt["value"][0],
                "group": group,
                "transformation_id": transformation_to_str(transformation_id),
                "type": "technosphere",
            }
            self.add_optional_fields(inpt, exchange)
            self.add_price(obj, exchange)
            self.add_cost(obj, exchange)
            exchange_list.append(exchange)

            for transport in inpt.get("transport", []):
                if "value" not in transport:
                    continue
                t_exchange = {
                    "name": transport["term"]["name"],
                    "term_type": transport["term"]["termType"],
                    "term_id": transport["term"]["@id"],
                    "unit": transport["term"].get("units"),
                    "amount": transport["value"],
                    "returnLegIncluded": transport["returnLegIncluded"],
                    "group": group,
                    "cycle_id": cycle_id,
                    "type": "technosphere",
                }
                for field in OPTIONAL_FIELDS:
                    if field in transport:
                        t_exchange[field] = transport[field]
                for orig, new in MAPPED_OPTIONAL_FIELDS.items():
                    if orig in transport:
                        t_exchange[new] = transport[orig]
                self.add_distance(transport, t_exchange)
                self.add_practices(source=transport, target=exchange)
                exchange_list.append(t_exchange)
        return exchange_list

    def add_practices(self, source: dict, target: dict) -> None:
        properties = []

        for practice in source.get("practices", []):
            if "value" in practice:
                properties.append(self.process_practice(practice))

        if properties:
            target["properties"] = properties

    def process_practice(self, obj: dict) -> dict:
        data = {
            "name": obj["term"]["name"],
            "term_type": obj["term"]["termType"],
            "term_id": obj["term"]["@id"],
            "unit": obj["term"].get("units"),
            "amount": obj["value"][0],
        }

        if "model" in obj:
            data["model"] = obj["model"]

        return data

    def get_products(
        self, obj: dict, cycle_id: str, transformation_id: Optional[str] = None
    ) -> Tuple[list, list]:
        new_exchanges, new_datasets = [], []

        for node in obj.get("products", []):
            if node["value"][0] == 0:
                continue

            if node.get("primary"):
                obj["reference product"] = node["term"]["name"]

            exchange = {
                "type": "production",
                "name": node["term"]["name"],
                "term_type": node["term"]["termType"],
                "term_id": node["term"]["@id"],
                "unit": node["term"].get("units"),
                "amount": node["value"][0],
                "transformation_id": transformation_to_str(transformation_id),
                "cycle_id": cycle_id,
            }

            product = {
                "name": node["term"]["name"],
                "term_type": node["term"]["termType"],
                "term_id": node["term"]["@id"],
                "unit": node["term"].get("units"),
                "transformation_id": transformation_to_str(transformation_id),
                "type": "product",
                "cycle_id": cycle_id,
            }

            self.add_price(node, product)
            self.add_optional_fields(node, product)

            new_exchanges.append(exchange)
            new_datasets.append(product)

        return new_exchanges, new_datasets

    def is_aggregated_emission(self, obj: dict) -> bool:
        """
        Mark emission as aggregated to avoid double counting.
        This is denoted by (e.g. an "ecoinvent" mention in the
        name within the Hestia database).
        """
        if "methodModel" not in obj:
            return False

        if any(
            term in obj["methodModel"].get("name", "").lower()
            for term in BACKGROUND_DATABASES
        ):
            return True

        return False

    def get_emissions(self, obj: dict) -> list:
        new_exchanges = []

        for em in obj.get("emissions", []):
            if self.is_aggregated_emission(em):
                continue
            elif em["value"][0] == 0:
                continue
            exchange = {
                "type": "biosphere",
                "name": em["term"]["name"],
                "term_type": em["term"]["termType"],
                "term_id": em["term"]["@id"],
                "unit": em["term"].get("units"),
                "amount": em["value"][0],
            }
            new_exchanges.append(exchange)

        return new_exchanges

    def get_transformations(self, obj: dict, cycle_id: str) -> list:
        new_datasets = []

        for source in obj.get("transformations", []):
            target = {
                "name": source["term"]["name"],
                "term_type": source["term"]["termType"],
                "term_id": source["term"]["@id"],
                "unit": source["term"].get("units"),
                "type": "process",
                "transformationId": transformation_to_str(source["transformationId"]),
                "cycle_id": cycle_id,
            }
            if "previousTransformationId" in source:
                target["previousTransformationId"] = transformation_to_str(
                    source["previousTransformationId"]
                )

            target["exchanges"] = self.get_inputs(
                source, cycle_id, source["transformationId"]
            )
            ne, nd = self.get_products(source, cycle_id, source["transformationId"])
            target["exchanges"].extend(ne)
            new_datasets.extend(nd)

            new_exchanges = self.get_emissions(source)
            target["exchanges"].extend(new_exchanges)

            new_datasets.append(target)

        return new_datasets


# utilities

MAPPED_OPTIONAL_FIELDS = {
    "description": "comment",
    "sd": "standard deviation",
    "min": "minimum",
    "max": "maximum",
    "statsDescription": "statistics",
}

OPTIONAL_FIELDS = {
    "startDate",
    "endDate",
    "methodClassification",
    "observations",
    "methodClassificationDescription",
    "model",
    "modelDescription",
    "revenue",
    "economicValueShare",
}

SUFFIXES = {"", "Sd", "Min", "Max", "StatsDefinition"}
PRICE = {"price" + suffix for suffix in SUFFIXES}
COST = {"cost" + suffix for suffix in SUFFIXES}
DISTANCE = {"distance" + suffix for suffix in SUFFIXES}
BACKGROUND_DATABASES = {
    "ecoinvent",
}
