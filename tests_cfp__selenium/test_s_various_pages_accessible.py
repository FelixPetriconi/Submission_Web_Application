from configuration import base_url

# NB PyCharm can't tell these are used as fixtures, but they are.
# NB server is an session scope autouse fixture that no test needs direct access to.
from fixtures import browser, server


def test_can_get_root(browser):
    browser.get(base_url)
    assert 'ACCU' in browser.page_source


def test_can_get_register_page_in_call_open_state(browser):
    browser.get(base_url + 'register')
    assert 'Register' in browser.page_source


def test_get_login_page_in_call_open_state(browser):
    browser.get(base_url + 'login')
    assert 'Login' in browser.page_source
