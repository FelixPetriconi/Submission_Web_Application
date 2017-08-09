def check_menu_items(driver, expected):
    menu = driver.find_element_by_id('navigation-links').text
    for item in expected:
        assert item in menu


def check_no_menu_items(driver):
    assert not driver.find_element_by_id('navigation-links').text
