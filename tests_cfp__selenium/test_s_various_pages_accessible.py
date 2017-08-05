from configuration import base_url

# NB PyCharm can't tell these are used as fixtures, but they are.
# NB server is an session scope autouse fixture that no test needs direct access to.
from fixtures import driver, server

# NB The server is in "call open" state.


def test_can_get_root_page(driver):
    driver.get(base_url)
    assert ' – Call for Proposals' in driver.page_source


def test_can_get_register_page(driver):
    driver.get(base_url + 'register')
    assert ' – Registration' in driver.page_source


def test_can_access_register_success_new_page(driver):
    driver.get(base_url + 'register_success_new')
    assert ' – Registration' in driver.page_source
    assert 'You have successfully registered' in driver.page_source


def test_can_access_register_success_update_page(driver):
    driver.get(base_url + 'register_success_update')
    assert ' – Registration' in driver.page_source
    assert 'Your account details were successful updated.' in driver.page_source


def test_can_get_login_page(driver):
    driver.get(base_url + 'login')
    assert ' – Login' in driver.page_source
