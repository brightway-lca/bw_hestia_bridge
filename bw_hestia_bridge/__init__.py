"""bw_hestia_bridge."""


__version__ = "0.1.0"


_config: dict = {
    "http_proxy": "",
    "https_proxy": "",
    "hestia_token": None,
    "hestia_api": "https://api.hestia.earth"
}


from .data_preparation import clean_background_emissions, clean_irrelevant_emissions
from .hestia_api import (
    get_hestia_node, login_to_hestia, search_hestia, set_hestia_token)
from .utils import get_config, save_config, set_config


__all__ = (
    "__version__",
    "clean_background_emissions",
    "clean_irrelevant_emissions",
    "get_config",
    "get_hestia_node",
    "login_to_hestia",
    "search_hestia",
    "set_config",
    "set_token"
)
