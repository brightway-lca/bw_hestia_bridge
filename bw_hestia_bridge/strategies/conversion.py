from collections import defaultdict
from functools import lru_cache
from typing import Optional, Tuple

from ..hestia_api import simple_hestia

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


class Converter:
    def __init__(self, staging: Optional[bool] = False) -> None:
        self.staging = staging

    def convert(self, source: dict) -> list:
        return_data = []

        target = self.get_basic_metadata(source)
        self.add_practices(source=source, target=target)
        if "animals" in source:
            target["animals"] = source["animals"]

        target["exchanges"] = self.get_inputs(source)
        new_exchanges, new_datasets = self.get_products(source)
        target["exchanges"].extend(new_exchanges)
        return_data.extend(new_datasets)

        return_data.append(target)

        # TBD: Make sure we aren't adding duplicate product nodes
        return return_data

    def get_basic_metadata(self, obj: dict) -> dict:
        EXTRAS = {
            "createdAt",
            "updatedAt",
            "endDate",
            "cycleDuration",
            "functionalUnit",
            "defaultMethodClassification",
            "defaultMethodClassificationDescription",
        }
        return {
            "@id": obj["@id"],
            "comment": obj.get("description"),
            "location": self.get_location(obj["site"]["@id"]),
            "type": "process",
            "extra_metadata": {key: obj[key] for key in EXTRAS if key in obj},
        }

    @lru_cache
    def get_location(self, node_id: str) -> str:
        return simple_hestia(node_type="site", node_id=node_id, staging=self.staging)[
            "name"
        ]

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

    def get_inputs(self, obj: dict) -> list:
        counter = defaultdict(int)

        exchange_list = []

        for inpt in obj["inputs"]:
            if "value" not in inpt:
                continue

            group = "{}-{}".format(inpt["term"]["name"], counter[inpt["term"]["name"]])
            counter[inpt["term"]["name"]] += 1

            exchange = {
                "name": inpt["term"]["name"],
                "term_type": inpt["term"]["termType"],
                "term_id": inpt["term"]["@id"],
                "unit": inpt["term"].get("units"),
                "amount": inpt["value"][0],
                "group": group,
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

    def get_products(self, obj: dict) -> Tuple[list, list]:
        new_exchanges, new_datasets = [], []

        for node in obj.get("products", []):
            if node["value"][0] == 0:
                continue
            if node.get("primary"):
                obj["reference product"] = node["term"]["name"]
            exchange = {
                "type": "production",
                "name": node["term"]["name"],
                "unit": node["term"].get("units"),
                "amount": node["value"][0],
            }
            product = {
                "name": node["term"]["name"],
                "term_type": node["term"]["termType"],
                "term_id": node["term"]["@id"],
                "unit": node["term"].get("units"),
            }
            self.add_price(node, product)
            self.add_optional_fields(node, product)

            new_exchanges.append(exchange)
            new_datasets.append(product)

        return new_exchanges, new_datasets
