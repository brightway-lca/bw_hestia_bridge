from bw2io import activity_hash


def add_code_from_hestia_attributes(data):
    FIELDS = ("name", "unit", "reference product", "transformation_id")

    for obj in data:
        obj["code"] = activity_hash(obj, fields=FIELDS)
    return data
