from bw_hestia_bridge import get_hestia_node, search_hestia, set_config


def test_search():
    '''
    Test the search function

    These tests are dependent on the Staging API of Hestia, if some things
    change on the Staging Server, they could fail. In such a case it could
    be convenient to disable these tests if reality demands a rapid merge.
    '''
    # test empty results
    assert not search_hestia("nonexistant")

    # test limits and nested search
    set_config("use_staging", True)

    assert len(search_hestia({"products.term.name": "Saplings"})) == 10
    assert len(search_hestia({"products.term.name": "Saplings"}, limit=12)) == 12

    # test combined queries
    assert 0 < len(search_hestia({"name": "ouidah", "products.term.name": "Saplings"})) < 10

    # test more or less precise match
    res_or = search_hestia(
        {"name": "conventional denmark", "product.term.name": "Maize"}, how="or")

    res_and = search_hestia(
        {"name": "conventional denmark", "product.term.name": "Maize"}, how="and")

    assert len(res_and) < len(res_or)

    # test exact match
    res_or = search_hestia(
        "Maize, grain, Denmark, 2009, Conventional-Non Irrigated")

    res_exact = search_hestia(
        "Maize, grain, Denmark, 2009, Conventional-Non Irrigated", how="exact")

    assert len(res_or) > 1 and len(res_exact) == 1

    # check exact with complex match
    assert len(search_hestia(
        {"inputs.term.name": 'Inorganic Nitrogen fertiliser, unspecified (kg N)'},
        how="exact")) > 0


def test_download():
    '''
    Download complete node information from Hestia

    These tests are dependent on the Staging API of Hestia, if some things
    change on the Staging Server, they could fail. In such a case it could
    be convenient to disable these tests if reality demands a rapid merge.
    '''
    set_config("use_staging", True)

    # test with search results
    res = search_hestia({"name": "ouidah", "products.term.name": "Saplings"})

    node = get_hestia_node(res[0])
    node_r = get_hestia_node(res[0], data_state="original")

    for k, v in res[0].items():
        if k in node:
            assert node[k] == v
            assert node_r[k] == v

    # test with node id and type
    nid = res[1]["@id"]
    ntype = res[1]["@type"]

    node = get_hestia_node(nid, ntype)

    for k, v in res[1].items():
        if k in node:
            assert node[k] == v
