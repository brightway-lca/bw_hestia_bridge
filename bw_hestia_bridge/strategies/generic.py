def drop_zeros(data: list) -> list:
    for ds in data:
        if "exchanges" in ds:
            ds["exchanges"] = [
                exc
                for exc in ds["exchanges"]
                if ("amount" not in exc or exc["amount"] != 0)
            ]
    return data
