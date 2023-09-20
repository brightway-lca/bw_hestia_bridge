import csv
from collections import defaultdict
from pathlib import Path
from typing import Optional
from uuid import uuid4

import bw2data as bd
from bw2io import activity_hash
from constructive_geometries import Geomatcher

DATA_DIR = Path(__file__).parent.parent.resolve() / "data"


def add_code_from_hestia_attributes(data: list) -> list:
    FIELDS = ("name", "unit", "reference product", "transformation_id")

    for obj in data:
        obj["code"] = activity_hash(obj, fields=FIELDS)
    return data


def link_ecoinvent_technosphere(data: list, ecoinvent_database_label: str) -> list:
    csv_fp = DATA_DIR / "ecoinvent_mappings_technosphere.csv"

    with open(csv_fp) as csvfile:
        reader = csv.reader(csvfile)
        # Skip header row
        next(reader)
        hestia_mapping = dict(reader)

    geo = Geomatcher()

    # Starts as Hestia @id to ecoinvent name
    # Switch to ecoinvent name to [@ids]
    hestia_reverse = defaultdict(list)

    for key, value in hestia_mapping.items():
        hestia_reverse[value].append(key)

    hestia_possibles = defaultdict(list)

    for ds in bd.Database(ecoinvent_database_label):
        for hestia_term_id in hestia_reverse.get(ds["name"], []):
            hestia_possibles[hestia_term_id].append(ds)

    for ds in data:
        try:
            overlapping = geo.within(ds["location"])[::-1]
        except KeyError:
            overlapping = []

        if ds.get("type", "process") != "process":
            continue
        for exc in ds.get("exchanges"):
            if exc["type"] == "technosphere" and "input" not in exc:
                pick_from_overlapping(
                    exc, hestia_possibles.get(exc["term_id"], []), overlapping
                )

    return data


def pick_from_overlapping(
    exc: dict,
    possibles: defaultdict,
    overlapping: list,
) -> None:
    """Try to find a provider of the supplied demand.

    `exc` is a dictionary; we use `term_id` (e.g. `manureSaltsKgK2O`) to search
    in `possibles`.

    `possibles` is a dictionary with keys of Hestia term `@id` keys, and values
    of bw2data processes which were mapped against the Hestia term ids in
    "ecoinvent_mappings_technosphere.csv".

    `overlapping` is an ordered list, from smallest to largest, or each region in
    ecoinvent which completely overlaps the `exc` dataset's location.

    We try to find the process in the correct `possibles` value list which most
    closely matches the `exc` dataset location. We also use fallback locations if
    necessary. The fallback locations are `RoE` (rest of Europe), `RoW` (rest of
    world), and `GLO` (global).

    If a match is found, adds `input` to the `exc`.

    """
    mapping = {ds["location"]: ds for ds in possibles}

    for location in overlapping:
        if location in mapping:
            exc["input"] = mapping[location].key
            return
    if (
        any("Europe" in geo for geo in overlapping) or ("RER" in overlapping)
    ) and "RoE" in mapping:
        exc["input"] = mapping["RoE"].key
    elif "RoW" in mapping:
        exc["input"] = mapping["RoW"].key
    elif "GLO" in mapping:
        exc["input"] = mapping["GLO"].key


def link_ecoinvent_biosphere(
    data: list, biosphere_label: Optional[str] = "biosphere3"
) -> list:
    csv_fp = DATA_DIR / "ecoinvent_mappings_biosphere.csv"

    with open(csv_fp) as csvfile:
        reader = csv.reader(csvfile)
        # Skip header row
        next(reader)
        hestia_mapping = {
            key: bd.get_node(code=value).key for key, value in reader if value
        }

    for ds in data:
        if ds.get("type", "process") != "process":
            continue
        for exc in ds.get("exchanges"):
            if exc.get("type") == "biosphere" and "input" not in exc:
                try:
                    exc["input"] = hestia_mapping[exc["term_id"]]
                except KeyError:
                    pass

    return data


def link_across_cycles(data: list) -> list:
    """Link across two cycles using the `graph_element` attribute.

    In this product:

    ```python
    {
        'name': 'Pig, piglet',
        'term_type': 'liveAnimal',
        'term_id': 'pigPiglet',
        'type': 'product',
        'cycle_id': 'baca63dqlc6n',
        'graph_element': {
            'from': {
                '@id': {'@id': 'baca63dqlc6n', '@type': 'Cycle'},
                '@type': 'Cycle'
            },
            'to': {
                '@id': '5-qkgrlriqqm',
                '@type': 'Cycle'
            },
            'via': {
                'term': {
                    '@type': 'Term',
                    'termType': 'liveAnimal',
                    'name': 'Pig, piglet',
                    '@id': 'pigPiglet'
                },
            '@type': 'Product'}
        }
    }
    ```

    We have a product (Pig, piglet) being produced by cycle `baca63dqlc6n` and used
    by cycle `5-qkgrlriqqm`.

    Here is the corresponding production exchanges in `baca63dqlc6n`:

    ```python
    {
        "type": "production",
        "name": "Pig, piglet",
        "term_type": "liveAnimal",
        "term_id": "pigPiglet",
        "unit": "number",
        "amount": 1,
        "transformation_id": null
    }
    ```

    And the consuming exchange in `5-qkgrlriqqm`:

    ```python
    {
        "name": "Pig, piglet",
        "cycle_id": "5-qkgrlriqqm",
        "term_type": "liveAnimal",
        "term_id": "pigPiglet",
        "unit": "number",
        "amount": 1.026,
        "group": "Pig, piglet-0",
        "type": "technosphere"
    }
    ```

    We normally only allow linking within one cycle, but in this case we need to
    link across cycles.
    """
    cross_cycle_products = {
        (
            ds["graph_element"]["via"]["term"]["@id"],
            ds["graph_element"]["to"]["@id"],
        ): (ds["database"], ds["code"])
        for ds in data
        if ds.get("type") == "product" and "graph_element" in ds
    }

    for ds in data:
        for exc in ds.get("exchanges", []):
            if exc.get("input") or not exc.get("type") == "technosphere":
                continue
            try:
                exc["input"] = cross_cycle_products[(exc["term_id"], exc["cycle_id"])]
            except KeyError:
                continue

    return data


def previous_transformation(val: str) -> str:
    # Definitely going to be punished in the afterlife for this...
    if val == "0":
        return "0"
    else:
        return str(int(val) - 1)


def link_to_previous_transformation(data):
    possibles = {
        (ds["term_id"], ds["cycle_id"], ds["transformation_id"]): (
            ds["database"],
            ds["code"],
        )
        for ds in data
        if ds.get("type") == "product"
    }

    for ds in data:
        for exc in ds.get("exchanges", []):
            if not exc.get("type") == "technosphere" or exc.get("input"):
                continue
            try:
                exc["input"] = possibles[
                    (
                        exc["term_id"],
                        exc["cycle_id"],
                        previous_transformation(exc["transformation_id"]),
                    )
                ]
            except KeyError:
                continue

    return data


def create_mocks(data):
    new_data = []

    for ds in data:
        for exc in ds.get("exchanges", []):
            if not exc.get("input") and exc.get("type") == "technosphere":
                code = uuid4().hex
                # TBD: We should check and not create multiple products for same flow
                part_one = {
                    "database": ds["database"],
                    "code": code,
                    "type": "product",
                    "name": "Mock " + exc["name"],
                    "mock": True,
                    "cycle_id": exc["cycle_id"],
                    "term_id": exc["term_id"],
                }
                part_two = {
                    key: exc.get(key)
                    for key in (
                        "cycle_id",
                        "transformation_id",
                        "term_id",
                        "unit",
                        "group",
                    )
                }
                new_data.append(part_one | part_two)
                exc["input"] = (ds["database"], code)
    data.extend(new_data)
    return data
