import time

import pytest

from flask import url_for

from configuration import base_url

# NB PyCharm can't tell these are used as fixtures, but they are.
# NB server is an session scope autouse fixture that no test needs direct access to.
from fixtures import browser, server


@pytest.fixture
def registrant():
    return {
        'email': 'a@b.c',
        'passphrase': 'Passphrase1',
        'cpassphrase': 'Passphrase1',
        'name': 'User Name',
        'phone': '+011234567890',
        'country': 'India',
        'state': 'TamilNadu',
        'postal_code': '123456',
        'town_city': 'Chennai',
        'street_address': 'Chepauk',
    }


def XXX_test_user_can_successfully_register(browser, registrant):
    browser.get(base_url + 'register')
    assert 'Registration' in browser.page_source
    for key, value in registrant.items():
        browser.find_element_by_id(key).send_keys(value)
    browser.find_element_by_id('submit').click()
    time.sleep(1)
    # assert 'success.html' in browser.current_url
    # assert 'You have successfully registered.' in browser.page_source
