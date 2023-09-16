from bw_hestia_bridge import search_hestia, set_config


def test_search():
    ''' Test the search function '''
    # test empty results
    assert not search_hestia("nonexistant")

    # test limits and nested search
    set_config("hestia_api", "https://api-staging.hestia.earth")

    assert len(search_hestia({"products.term.name": "Saplings"})) == 10
    assert len(search_hestia({"products.term.name": "Saplings"}, limit=20)) == 20

    # test combined queries
    assert 0 < len(search_hestia({"name": "ouidah", "products.term.name": "Saplings"})) < 10

    # test precise match
    res_fuzzy = search_hestia(
        {"name": "conventional denmark", "product.term.name": "Maize"},
        match_all_words=False)

    res_exact = search_hestia(
        {"name": "conventional denmark", "product.term.name": "Maize"},
        match_all_words=True)

    assert len(res_exact) < res_fuzzy
