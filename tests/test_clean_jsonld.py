from bw_hestia_bridge import clean_background_emissions


def test_num_emissions(banana):
    assert len(banana["emissions"]) == 126


def test_num_emissions_after_cleaning(banana):
    data = clean_background_emissions(banana)
    assert len(data["emissions"]) == 72
