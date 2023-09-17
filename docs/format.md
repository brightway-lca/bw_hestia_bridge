# Mapping the data format

## Basic process data

Brightway will pull the follow attributes verbatim:

```python
{
    "@id": str,
    "description": str,  # But we label as comment
}
```

The following attributes will be put in a new `extra_metadata` dictionary:

```python
{
    "extra_metadata": {
        "createdAt": str,
        "updatedAt": str,
        "endDate": str,
        "cycleDuration": int,
        "functionalUnit": str,
        "defaultMethodClassification": str,
        "defaultMethodClassificationDescription": str,
    }
}
```

## `site`

Here we need to look up more information. So when we get:

```python
  "site": {
    "@type": "Site",
    "@id": "k-dc9b3ii8uw"
  },
```

We can query `https://api-staging.hestia.earth/sites/k-dc9b3ii8uw` and get:

```python
{
    '@context': 'https://www-staging.hestia.earth/schema/Site.jsonld',
    'createdAt': '2023-09-14',
    'updatedAt': '2023-09-15',
    '@id': 'k-dc9b3ii8uw',
    '@type': 'Site',
    'defaultSource': {
        '@id': 'ejhl-3wf1lvh',
        '@type': 'Source'
    },
    'siteType': 'cropland',
    'country': {
        '@type': 'Term',
        'termType': 'region',
        'name': 'Colombia',
        '@id': 'GADM-COL'
    },
    'name': 'Cropland - Colombia',
    'schemaVersion': '23.1.0',
    'originalId': 'colombia'
}
 ```

 We only need to take the `name`, so would add `"location": "Colombia"`

## `practices`

We take only the valued practices (i.e. those with a `value` attribute, and label these as `properties`. This is consistent with the way we import properties from the ecospold2 format.

We re-label a lot here to make the data feel more like Brightway inventory datasets:

```python
for practice in cycle['practices']:
    if 'value' not in practice:
        continue
    prperty = {
        'name': practice['term']['name'],
        'term_type': practice['term']['termType'],
        'term_id': practice['term']['@id'],
        'unit': practice['term'].get("units"),
        'amount': practice['value'][0],
    }
    if 'model' in practice:
        prperty['model'] = practice['model']
```

We then add a list of `prperty` instances as `"properties"`.

## `animals`

If the `animals` attribute is present in a cycle, we take it without modification, but do not use any of its data during the import.

## `inputs`

Each element in the `inputs` array maps to a technosphere input exchange. We won't import all the Hestia data.

We take only the valued practices (i.e. those with a `value` attribute. If there is not numeric value, we have nothing to insert into the matrix.

```python
from collections import defaultdict

MAPPED_OPTIONAL_FIELDS = {
    'description': 'comment',
    'sd': 'standard deviation',
    'min': 'minimum',
    'max': 'maximum',
    'statsDescription': 'statistics',
}
OPTIONAL_FIELDS = {
    'startDate',
    'endDate',
    'methodClassification',
    'observations',
    'methodClassificationDescription',
    'model',
    'modelDescription',
}
SUFFIXES = {'', 'Sd', 'Min', 'Max', 'StatsDefinition'}
PRICE = {'price' + suffix for suffix in SUFFIXES}
COST = {'cost' + suffix for suffix in SUFFIXES}
DISTANCE = {'distance' + suffix for suffix in SUFFIXES}

counter = defaultdict(int)

for inpt in cycle['inputs']:
    if 'value' not in inpt:
        continue

    group = "{}-{}".format(
        inpt['term']['name'],
        counter[inpt['term']['name']]
    )
    counter[inpt['term']['name']] += 1

    exchange = {
        'name': inpt['term']['name'],
        'term_type': inpt['term']['termType'],
        'term_id': inpt['term']['@id'],
        'unit': inpt['term'].get("units"),
        'amount': inpt['value'][0],
        'group': group,
    }
    for field in OPTIONAL_FIELDS:
        if field in inpt:
            exchange[field] = inpt[field]
    for orig, new in MAPPED_OPTIONAL_FIELDS.items():
        if orig in inpt:
            exchange[new] = inpt[orig]
    if 'price' in inpt:
        exchange['price'] = {key: inpt[key] for key in PRICE if key in inpt}
        if 'currency' in inpt:
            exchange['price']['currency'] = inpt['currency']
    if 'cost' in inpt:
        exchange['cost'] = {key: inpt[key] for key in COST if key in inpt}
        exchange['cost']['currency'] = inpt['currency']
```

### `transport` in `inputs`

Hestia includes an optional list of transport inputs attached to another input, but we need a flat list of technosphere input exchanges. We therefore unroll the optional `transport` attribute.

Hestia includes emissions and inputs (e.g. diesel) to transport, but the intent of this importer is to link these to the original background data sources, so we do not include the Hestia fuel consumption or direct emissions.

We will store the connection between transport inputs and their parent inputs using the `group` field.

Transport `value` fields are always in ton-kilometers, but are somehow optional. We skip those for which we don't have a `value` field, as we can't use them in inventory modelling.

```python
DISTANCE = {'distance' + suffix for suffix in SUFFIXES}

for inpt in cycle['inputs']:
    ...

    if 'transport' in inpt:
        for transport in inpt['transport']:
            if 'value' not in transport:
                continue
            exchange = {
                'name': transport['term']['name'],
                'term_type': transport['term']['termType'],
                'term_id': transport['term']['@id'],
                'unit': transport['term'].get("units"),
                'amount': transport['value'],
                'returnLegIncluded': transport['returnLegIncluded'],
                'group': group,
            }
            for field in OPTIONAL_FIELDS:
                if field in transport:
                    exchange[field] = transport[field]
            for orig, new in MAPPED_OPTIONAL_FIELDS.items():
                if orig in transport:
                    exchange[new] = transport[orig]
            if 'distance' in transport:
                exchange['distance'] = {key: transport[key] for key in DISTANCE if key in transport}
```

We also take the `practices` as properties, as above.

## `products`

We will construct a supply chain of `process` nodes, which will produce `products`, and consume `products` (if coming from other Hestia cycles) or `processes` (if coming from a background database). For each `product`, we therefore need to create a new inventory dataset with the type `product`. But we also need to add a production exchange to the cycle unit process.

```python
```
