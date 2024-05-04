# Tutorial

This is a quick overview of the main functions of `bw_hestia_bridge`.

## Getting started

Once you\'ve installed `bw_hestia_bridge`, open a python or
[ipython](https://ipython.readthedocs.io)/[jupyter](https://jupyter.org)
input and type: :

```python
import bw_hestia_bridge as bhb
```

You can now access all the functions via the `bhb` object.

## Searching the Hestia database

To find elements in the Hestia database, you can use the
`~bw_hestia_bridge.search_hestia`{.interpreted-text role="func"}
function :

```python
# search for a name
res = bhb.search_hestia("Wheat")
print(f"Got {len(res)} results")  # 10 results by default
print(res)
```

To get more results, use the `limit` argument :

```python
# get more results
res = bhb.search_hestia("Wheat", limit=15)
print(f"Got {len(res)} results")  # got 15 results
```

You can also search specific types of objects, like \"cycles\" :

```python
bhb.search_hestia("Wheat", node_type="cycle")
```

If you want to search for a field other than the node \"name\", you can
also specify it in the query. For instance, to get nodes of a given
type, regardless of their name, use :

```python
bhb.search_hestia({"@type": "term"}, limit=10000)  # get all possible terms
```

Note that if the are more than 10000 elements, it will not be possible
to get all of them due to an intrinsic limitation in ElasticSearch
queries on the [Hestia](https://hestia.earth) database.

For more complex queries, check the examples given in the docstring of
`~bw_hestia_bridge.search_hestia`{.interpreted-text role="func"}.

## Converting Hestia data to Brightway

We provide the `~bw_hestia_bridge.HestiaImporter`{.interpreted-text
role="class"} class to convert Hestia data into a Brightway-usable
database. From a Hestia [Cycle](https://www.hestia.earth/schema/Cycle)
(the equivalent of a Brightway process), you can generate a new database
that should contain the supply-chain necessary to run an LCA.

:::{warning}
At the moment, this is a work in progress and the results will probably not deliver a working database.
:::

```python
eidb_name = "ei39"  # the name of your EcoInvent database
cycle_id = "ztqcopzc7qpl"  # a cycle you found via ``search_hestia``
imp = bhb.HestiaImporter(cycle_id=cycle_id, ecoinvent_label=eidb_name)
imp.apply_strategies()
print(imp.statistics())
```

If the number of \"unlinked exchanges\" is zero, you can then save the
database via :

```python
imp.write_database(db_name="your-db-name")
```

## Download the whole node data from Hestia

You can get the data directly from the search results :

```python
res = bhb.search_hestia("Wheat", node_type="cycle")
bhb.get_hestia_node(res[0])
```

Otherwise, you can get a node from its ID and type :

```python
nid = "75eszetffr_n"
ntype = "cycle"
bhb.get_hestia_node(nid, ntype)

# or, without the type
bhb.get_hestia_node(nid)
```

:::{note}
Though the second case may seem more convenient, it will require two
calls to the Hestia API instead of a single one, so it might become
significantly slower when used in loops (providing both ID and type
should be prefered in that case).
:::

## Configuring `bw_hestia_bridge`

The package uses a config file that can be updated and saved so that you
don\'t need to change the settings everytime. You can check the config
via :

```python
bhb.get_config()
```

Main settings are for proxies and \"use_staging\", which will switch
between the stable and the staging API of Hestia. To switch to staging,
just use :

```python
bhb.set_config("use_staging", True)
```

Note that if you prefer, it will autodect the \"use_staging\"
environment variable.

If you want this change to be persistent, just call :

```python
bhb.save_config()
```

And you're done.
