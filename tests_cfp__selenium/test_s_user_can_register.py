import time

import pytest

# NB server is an session scope autouse fixture that no test needs direct access to.
from common import base_url, browser, server


@pytest.fixture
def registrant():
    return {
        'email': 'a@b.c',
        'passphrase': 'Passphrase1',
        'name': 'User Name',
        'phone': '+011234567890',
        'country': 'India',
        'state': 'TamilNadu',
        'postalcode': '123456',
        'towncity': 'Chennai',
        'streetaddress': 'Chepauk',
        'captcha': '1',
        'question': '12',
    }


def test_user_can_successfully_register(browser, registrant):
    browser.get('/register')
    time.sleep(1)

    browser.find_element_by_id('email').send_keys(registrant['email'])
    browser.find_element_by_id('name').send_keys(registrant['name'])
    browser.find_element_by_id('password').send_keys(registrant['password'])
    browser.find_element_by_id('cpassword').send_keys(registrant['password'])
    browser.find_element_by_id('submit').click()
    time.sleep(1)

    assert url_for('index') in browser.current_url
    assert 'You have successfully registered.' in browser.find_element_by_class_name('alert').text

    # TODO Assert the person is in the database
