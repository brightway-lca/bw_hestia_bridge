import csv
from collections import defaultdict
from pathlib import Path
from typing import Optional

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
