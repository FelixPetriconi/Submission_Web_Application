from common import base_url, browser, server


def test_can_get_root(browser, server):
    browser.get(base_url)
    assert 'ACCU' in browser.page_source


def test_get_login_page_in_call_open_state(browser, server):
    browser.get(base_url + 'login')
    assert 'Login' in browser.page_source
