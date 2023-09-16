# Mapping the data format

## Basic process data

Brightway will pull the follow attributes verbatim:

```python
{
    "@id": str,
    "description": str,
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

## `inputs`

Each element in the `inputs` array maps to a technosphere exchange.
