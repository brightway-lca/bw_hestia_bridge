import os

os.environ["use_staging"] = "false"
os.environ["http_proxy"] = ""

import pytest

import bw_hestia_bridge as bhb


def test_config():
    config = bhb.get_config()

    assert not bhb.get_config("use_staging")

    config["use_staging"] = True

    bhb.set_config(config)

    assert bhb.get_config("use_staging")

    bhb.set_config("use_staging", False)

    assert not bhb.get_config("use_staging")

    bhb.save_config()

    with pytest.raises(KeyError):
        bhb.set_config("what's the answer", 42)
