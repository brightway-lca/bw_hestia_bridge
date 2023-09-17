import requests
import pandas as pd
from io import StringIO


def create_ecoinvent_mappings():
    # list of term types that use ecoinvent processes
    term_types = [
        "antibiotic",
        "electricity",
        "fertiliserBrandName",
        "fuel",
        "inorganicFertiliser",
        "material",
        "soilAmendment",
        "transport",
    ]

    def fetch_ecoinvent_lookup(term_type):
        URL = f"https://www.hestia.earth/glossary/lookups/{term_type}.csv"
        response = requests.get(URL)
        data = StringIO(response.text)
        lookup = (
            pd.read_csv(data)[["term.id", "ecoinventMapping"]]
            .set_index("term.id")
            .dropna()
        )
        return lookup["ecoinventMapping"]

    ecoinvent_mappings_per_term_type = []

    for term_type in term_types:
        ecoinvent_mappings_per_term_type.append(fetch_ecoinvent_lookup(term_type))

    ecoinvent_mappings = pd.concat(ecoinvent_mappings_per_term_type)

    # Applying some general rules to tidy up the ecoinvent names
    ecoinvent_mappings = ecoinvent_mappings.str.replace(
        r"^.*?(?=market)", "", regex=True
    )
    ecoinvent_mappings = ecoinvent_mappings.str.replace(r":.*$", "", regex=True)
    ecoinvent_mappings = ecoinvent_mappings.str.replace(
        r"^.*?(?=electricity production)", "", regex=True
    )

    # The rest is renamed manually:
    renaming_dict = {
        "market for potassium sulfate, as K2O": "market for potassium sulfate",
        "market for phosphate fertiliser, as P2O5": "market for inorganic phosphorus fertiliser, as P2O5",
        "nitrogen fertiliser, as N, diammonium phosphate production": "diammonium phosphate production",
        "phosphate fertiliser, as P2O5, single superphosphate production": "single superphosphate production",
        "market for potassium chloride, as K2O": "market for potassium chloride",
        "market for transport, freight, light commercial vehicle": "market for transport, freight, lorry >32 metric ton, EURO5",
        "market for ammonium sulfate, as N": "market for ammonium sulfate",
        "nitrogen fertiliser, as N, monoammonium phosphate production": "monoammonium phosphate production",
        "market for urea, as N": "market for urea",
        "market for potassium fertiliser, as K2O": "market for inorganic potassium fertiliser, as K2O",
        "phosphate fertiliser, as P2O5, diammonium phosphate production": "diammonium phosphate production",
        "phosphate fertiliser, as P2O5, monoammonium phosphate production": "monoammonium phosphate production",
        "transport, freight train, transport, freight train, electricity": "transport, freight train, electricity",
        "market for phosphate rock, as P2O5, beneficiated, dry": "market for phosphate rock, beneficiated",
        "market for nitrogen fertiliser, as N": "market for inorganic nitrogen fertiliser, as N",
        "polyethylene, low density, granulate, polyethylene production, low density, granulate": "polyethylene production, low density, granulate",
        "nitrogen fertiliser, as N, urea ammonium nitrate production": "urea ammonium nitrate production",
        "phosphate fertiliser, as P2O5, triple superphosphate production": "triple superphosphate production",
        "market for transport, freight, sea, transoceanic ship with reefer, cooling": "market for transport, freight, sea, container ship with reefer, cooling",
        "transport, freight train, transport, freight train, diesel, with particle filter": "transport, freight train, diesel, with particle filter",
        "market for transport, freight, sea, transoceanic ship with reefer, freezing": "market for transport, freight, sea, container ship with reefer, freezing",
        "market for ammonium nitrate, as N": "market for ammonium nitrate",
    }
    ecoinvent_mappings = ecoinvent_mappings.replace(renaming_dict)

    return ecoinvent_mappings


create_ecoinvent_mappings().to_csv("ecoinvent_mappings.csv")
