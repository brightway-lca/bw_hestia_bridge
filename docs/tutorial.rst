========
Tutorial
========

This is a quick overview of the main functions of ``bw_hestia_bridge``.


Getting started
===============

Once you've installed ``bw_hestia_bridge``, open a python or ipython_/jupyter_ input and type: ::

    import bw_hestia_bridge as bhb

You can now access all the functions via the ``bhb`` object.


Searching the Hestia database
=============================

To find elements in the Hestia database, you can use the
:func:`~bw_hestia_bridge.search_hestia` function ::

    # search for a name
    res = bhb.search_hestia("Wheat")
    print(f"Got {len(res)} results")  # 10 results by default
    print(res)

To get more results, use the ``limit`` argument ::

    # get more results
    res = bhb.search_hestia("Wheat", limit=15)
    print(f"Got {len(res)} results")  # got 15 results

You can also search specific types of objects, like "cycles" ::

    bhb.search_hestia("Wheat", node_type="cycle")

If you want to search for a field other than the node "name", you can also
specify it in the query.
For instance, to get nodes of a given type, regardless of their name, use ::

    bhb.search_hestia({"@type": "term"}, limit=10000)  # get all possible terms

Note that if the are more than 10000 elements, it will not be possible to
get all of them due to an intrinsic limitation in ElasticSearch queries on
the Hestia_ database.

For more complex queries, check the examples given in the docstring of
:func:`~bw_hestia_bridge.search_hestia`.


Download the whole node data from Hestia
========================================

You can get the data directly from the search results ::

    res = bhb.search_hestia("Wheat", node_type="cycle")
    bhb.get_hestia_node(res[0])

Otherwise, you can get a node from its ID and type ::

    nid = "75eszetffr_n"
    ntype = "cycle"
    bhb.get_hestia_node(nid, ntype)


.. _ipython: https://ipython.readthedocs.io
.. _jupyter: https://jupyter.org
.. _Hestia: https://hestia.earth


Configuring ``bw_hestia_bridge``
================================

The package uses a config file that can be updated and saved so that you don't
need to change the settings everytime.
You can check the config via ::

    bhb.get_config()

Main settings are for proxies and "use_staging", which will switch between the
stable and the staging API of Hestia.
To switch to staging, just use ::

    bhb.set_config("use_staging", True)

Note that if you prefer, it will autodect the "use_staging" environment
variable.

If you want this change to be persistent, just call ::

    bhb.save_config()

And you're done.
