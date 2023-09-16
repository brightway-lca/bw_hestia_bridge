import json
import os

from typing import Any, Union, Optional

from platformdirs import user_config_dir

import bw_hestia_bridge as bhb


confdir = user_config_dir("bw_hestia_bridge", appauthor=False)
os.makedirs(confdir, exist_ok=True)

conf_file = os.path.join(confdir, "config.json")


def _init_config():
    ''' Create or set the config from the file and the environment '''
    config = bhb._config.copy()

    if os.path.isfile(conf_file):
        with open(conf_file, "r") as f:
            new_config = json.load(f)

            for k, v in new_config.items():
                config[k] = v
    else:
        with open(conf_file, "w") as f:
            json.dump(config, f)

    # auto-set proxies if environment variables are set
    proxies = ["http_proxy", "https_proxy"]

    for p in proxies:
        if p in os.environ or p.upper() in os.environ:
            if not config[p]:
                config[p] = os.environ.get(p, os.environ[p.upper()])

    # get API url and token from the environment if present
    for key in ("hestia_token", "hestia_api"):
        config[key] = os.environ.get(key, config[key])

    set_config(config)


def get_config(param: Optional[str] = None) -> Any:
    ''' Return the config settings '''
    config = bhb._config.copy()

    if param:
        return config[param]

    return config


def set_config(
    config : Union[str, dict],
    value : Optional[str] = None
) -> None:
    '''
    Set configuration.

    Parameters
    ----------
    config : str or dict
        Either a full configuration dict or the name of a configuration entry
        to set.
    value : str, optional
        If `config` is a string, `value` associated to this configuration entry.
    '''
    if isinstance(config, str):
        if config in bhb._config:
            bhb._config[config] = value
        else:
            raise KeyError(f"No '{config}' entry in configuration.")
    else:
        for k, v in config.items():
            set_config(k, v)
