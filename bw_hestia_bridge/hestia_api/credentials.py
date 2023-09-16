import requests

from typing import Optional

from .base_data import base_api_data
from ..utils import set_config


def login_to_hestia(email: str, pwd: str) -> None:
    '''
    Login to Hestia and get token.
    '''
    url, _, proxies, _ = base_api_data()

    headers = headers = {"Content-Type": "application/json"}

    data = {"email": email,"password": pwd}

    token = requests.post(
        f"{url}/users/signin", json=data, headers=headers
    ).json().get('token')

    set_hestia_token(token)


def set_hestia_token(token: str) -> None:
    '''
    Store the token in the config.
    '''
    set_config("hestia_token", token)
