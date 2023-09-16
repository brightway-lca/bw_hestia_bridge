def clean_background_emissions(obj: dict) -> dict:
    """
    Removed [background](https://www-staging.hestia.earth/schema/Emission#methodTier) emissions from aggregated input activities in the same dataset.

    Parameters
    ----------
    obj : dict
        The input dataset in Hestia JSON-LD format

    Returns
    -------
    obj : dict
        The same object, with the number of `emissions` possibly reduced

    """
    obj["emissions"] = [
        node for node in obj["emissions"] if node.get("methodTier") == "background"
    ]
    return obj
