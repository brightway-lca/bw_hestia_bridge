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

## Using the API

API key for development: 6t7B6uAwwZYjF5SJKGwLz5XmArsz894N8gio1UKVrj9K

Programmatic overview: https://www.hestia.earth/docs/#overview

Swagger: https://api.hestia.earth/swagger/

API Base URL: https://api-staging.hestia.earth/

Get a basic JSON LD:

```python
import requests
cycle_id = "help me!"
URL = "https://api-staging.hestia.earth/cycles/{cycle_id}/cycles"
requests.get(URL).json()
```

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
