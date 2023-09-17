from functools import lru_cache
from typing import Optional

from ..hestia_api import simple_hestia


class Converter:
    def __init__(self, staging: Optional[bool] = False) -> None:
        self.staging = staging

    def convert(self, obj: dict) -> list:
        return_data = []

        node = self.get_basic_metadata(obj)
        self.add_practices(node)
        if "animals" in obj:
            node["animals"] = obj["animals"]

        return_data.append(node)
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
            "extra_metadata": {key: obj[key] for key in EXTRAS if key in obj},
        }

    @lru_cache
    def get_location(self, node_id: str) -> str:
        return simple_hestia(node_type="site", node_id=node_id, staging=self.staging)[
            "name"
        ]

    def add_practices(self, obj: dict) -> dict:
        properties = []

        for practice in obj.get("practices", []):
            if "value" in practice:
                properties.append(self.process_practice(practice, False))

        if properties:
            obj["properties"] = properties
        return obj

    def process_practice(self, obj: dict, single_amount: bool) -> dict:
        data = {
            "name": obj["term"]["name"],
            "term_type": obj["term"]["termType"],
            "term_id": obj["term"]["@id"],
            "unit": obj["term"].get("units"),
            "amount": obj["value"] if single_amount else obj["value"][0],
        }
        if "model" in obj:
            data["model"] = obj["model"]
        return data
