from bw_hestia_bridge import clean_background_emissions, clean_irrelevant_emissions


def test_num_emissions(banana):
    assert len(banana["emissions"]) == 126


def test_num_emissions_after_cleaning_background(banana):
    data = clean_background_emissions(banana)
    assert len(data["emissions"]) == 126 - 72


def test_num_emissions_after_cleaning_not_relevant(banana):
    data = clean_irrelevant_emissions(banana)
    assert len(data["emissions"]) == 126 - 11
