import bw_hestia_bridge as bhb

stable_url = "https://api.hestia.earth"
staging_url = "https://api-staging.hestia.earth"


def base_api_data() -> tuple[str, dict, dict]:
    """Return the data necessary to query the Hestia API"""
    config = bhb.get_config()

    url = staging_url if config["use_staging"] else stable_url

    proxies = {
        "http": config["http_proxy"],
        "https": config["https_proxy"],
    }

    headers = {"Content-Type": "application/json"}

    return url, proxies, headers


# Hestia database information

valid_types = {
    "actor",
    "animal",
    "bibliography",
    "completeness",
    "cycle",
    "emission",
    "impactassessment",
    "indicator",
    "infrastructure",
    "input",
    "management",
    "measurement",
    "organisation",
    "practice",
    "product",
    "property",
    "site",
    "source",
    "term",
    "transformation",
    "transport",
}

nested_elements = {
    'inputs',
    'practices',
    'otherSites',
    'animals',
    'products',
    'transformations',
    'emissions',
    'emissionsResourceUse',
    'impacts',
    'endpoints',
    'measurements',
    'management',
    'metaAnalyses',
    'subClassOf',
    'defaultProperties'
}
