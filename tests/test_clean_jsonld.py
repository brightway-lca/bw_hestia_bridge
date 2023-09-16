from bw_hestia_bridge import clean_background_emissions, clean_irrelevant_emissions


def test_num_emissions(banana, pigs):
    assert len(banana["emissions"]) == 126
    assert len(pigs["emissions"]) == 205


def test_num_emissions_after_cleaning_background(banana, pigs):
    data = clean_background_emissions(banana)
    assert len(data["emissions"]) == 54
    data = clean_background_emissions(pigs)
    assert len(data["emissions"]) == 83


def test_num_emissions_after_cleaning_not_relevant(banana, pigs):
    data = clean_irrelevant_emissions(banana)
    assert len(data["emissions"]) == 115
    data = clean_irrelevant_emissions(pigs)
    assert len(data["emissions"]) == 144
