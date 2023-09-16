import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent.resolve() / "fixtures"


@pytest.fixture(scope="function")
def banana():
    return json.load(open(FIXTURES / "bananas.jsonld"))
