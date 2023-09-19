import json
import os
from typing import Any, Optional, Union

from platformdirs import user_config_dir

_config: dict = {
    "http_proxy": "",
    "https_proxy": "",
    "use_staging": False,
}


confdir = user_config_dir("bw_hestia_bridge", appauthor=False)
os.makedirs(confdir, exist_ok=True)

conf_file = os.path.join(confdir, "config.json")


def _init_config():
    """Create or set the config from the file and the environment"""
    config = _config.copy()

    overwrite = True

    if os.path.isfile(conf_file):
        with open(conf_file, "r") as f:
            new_config = json.load(f)

            if set(new_config) == set(config):
                overwrite = False

                for k, v in new_config.items():
                    config[k] = v

    if overwrite:
        # config file does not exist or config structure was changed
        # and should be overwritten
        save_config(config)

    # auto-set proxies if environment variables are set
    proxies = ["http_proxy", "https_proxy"]

    for p in proxies:
        if p in os.environ or p.upper() in os.environ and not config[p]:
            config[p] = os.environ.get(p, os.environ.get(p.upper(), ""))

    # get use_staging from environment if present
    if "use_staging" in os.environ:
        config["use_staging"] = \
            os.environ["use_staging"].lower() in ("1", "true")

    set_config(config)


def get_config(param: Optional[str] = None) -> Any:
    """Return the config settings"""
    config = _config.copy()

    if param:
        return config[param]

    return config


def set_config(config: Union[str, dict], value: Union[str, bool, None] = None) -> None:
    """
    Set configuration.

    Parameters
    ----------
    config : str or dict
        Either a full configuration dict or the name of a configuration entry
        to set.
    value : str, optional
        If `config` is a string, `value` associated to this configuration entry.
    """
    if isinstance(config, str):
        if config in _config:
            _config[config] = value
        else:
            raise KeyError(f"No '{config}' entry in configuration.")
    else:
        for k, v in config.items():
            set_config(k, v)


def save_config(config: Optional[dict] = None) -> None:
    """
    Save the the configuration.

    Parameters
    ----------
    config : dict, optional (default: current configuration)
        Configuration to save.
    """
    config = config or _config

    with open(conf_file, "w") as f:
        json.dump(config, f)
