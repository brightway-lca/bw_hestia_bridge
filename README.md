# bw_hestia_bridge

[![PyPI](https://img.shields.io/pypi/v/bw_hestia_bridge.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/bw_hestia_bridge.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/bw_hestia_bridge)][pypi status]
[![License](https://img.shields.io/pypi/l/bw_hestia_bridge)][license]

[![Read the documentation at https://bw_hestia_bridge.readthedocs.io/](https://img.shields.io/readthedocs/bw_hestia_bridge/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/brightway-lca/bw_hestia_bridge/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/brightway-lca/bw_hestia_bridge/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/bw_hestia_bridge/
[read the docs]: https://bw_hestia_bridge.readthedocs.io/
[tests]: https://github.com/brightway-lca/bw_hestia_bridge/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/brightway-lca/bw_hestia_bridge
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Installation

You can install _bw_hestia_bridge_ via [pip] from [PyPI]:

```console
$ pip install bw_hestia_bridge
```

## Functions

```python
def search_hestia(element: str, filter_type) -> list[dict[str, str]]:
    ''' Search the Hestia database. '''

def get_hestia_node(node: dict[str, str]) -> dict:
    ''' Download the Hestia node associated to `node`. '''

def login_to_hestia(email: str, password: str) -> None:
    ''' Register to Hestia and set the token '''

def set_hestia_token(token: str) -> None:
    ''' Set the token to call the Hestia API '''
```

## Using the Hestia API

Programmatic overview: https://www.hestia.earth/docs/#overview

Swagger: https://api.hestia.earth/swagger/

API Base URL: https://api-staging.hestia.earth/

Get a basic JSON LD:

```python
import requests
cycle_id = "cx_dtpwud1iu"
URL = "https://api-staging.hestia.earth/cycles/{cycle_id}/cycles"
requests.get(URL).json()
```

## Mapping `Hestia` cycles to the Brightway mental model

Hestia is not a linked network of unit processes, but detailed data on specific production systems. As they are agricultural, almost all of these systems have multiple outputs, and many of these outputs require further treatment. For example, in the [pig system](https://www-staging.hestia.earth/cycle/5-qkgrlriqqm?dataState=recalculated), there are three types of excreta produced, which go to deep bedding, which go to composting. Hestia doesn't seem to have a waste treatment for the final processed excreta.

Because these follow-on activities (Hestia calls them [Transformations](https://www-staging.hestia.earth/schema/Transformation)) are multi-input *and* multi-output, and because there is no guarantee that the respective ratios of these outputs align with the next stage inputs, we will do the following:

For each `transformation`, we create a new unit process. The *reference product* of this process will be the output with the highest mass.

For the other outputs, we will create proxy treatment activities. These proxies will handle any potential stoichiometric disparities.

If a `transformation` is a leaf node, i.e. it has inputs but no consumers for each outputs, we will create proxy consumers for each output other than the reference product.

We then go back to the original unit process, and add proxy consumers for each output which is not the reference product (i.e. marked `"primary": true`) or the reference product of a waste treatment.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_bw_hestia_bridge_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.


<!-- github-only -->

[command-line reference]: https://bw_hestia_bridge.readthedocs.io/en/latest/usage.html
[license]: https://github.com/brightway-lca/bw_hestia_bridge/blob/main/LICENSE
[contributor guide]: https://github.com/brightway-lca/bw_hestia_bridge/blob/main/CONTRIBUTING.md
