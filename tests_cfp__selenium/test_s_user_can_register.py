import pytest

from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ecs

from configuration import base_url

# NB PyCharm can't tell these are used as fixtures, but they are.
# NB server is an session scope autouse fixture that no test needs direct access to.
from fixtures import driver, server

# NB The server is in "call open" state.


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


def submit_data_to_register_page(driver, registrant):
    driver.get(base_url + 'register')
    assert ' – Registration' in driver.find_element_by_class_name('pagetitle').text
    for key, value in registrant.items():
        driver.find_element_by_id(key).send_keys(value)
    button = WebDriverWait(driver, 1).until(ecs.element_to_be_clickable((By.ID, 'submit')))
    assert 'Register' in button.text
    assert 'registerUser()' in button.get_attribute('onclick')
    button.click()


def XXX_test_user_can_successfully_register(driver, registrant):
    submit_data_to_register_page(driver, registrant)
    element = WebDriverWait(driver, 2).until(
        ecs.presence_of_element_located((By.CLASS_NAME, 'pagetitle'))
    )
    assert 'XXXX' in driver.find_element_by_id('content').text
    assert 'Registration Success' in element.text


@pytest.mark.parametrize(('key', 'value', 'message'), (
    ('email', 'a.b.c', 'Email should be of the format user@example.com'),
    ('passphrase', 'hum', 'Passphrase and confirmation passphrase not the same.'),
    ('cpassphrase', 'dedum', 'Confirmation passphrase is not valid.'),
    ('name', 'R', 'Invalid name.'),
    ('phone', 'blurb', 'Invalid phone number.'),
    ('postal_code', 'Fubar', 'Invalid postal code.'),
    # ('country', 'Fubar', 'Invalid country.'),
))
def test_single_error_causing_local_failure(key, value, message, driver, registrant, monkeypatch):
    monkeypatch.setitem(registrant, key, value)
    submit_data_to_register_page(driver, registrant)
    wait = WebDriverWait(driver, 2)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration'))
    # wait.until(ecs.text_to_be_present_in_element((By.ID, 'alert'), 'Problem with form, not submitting.'))
    wait.until(ecs.text_to_be_present_in_element((By.ID, key + '_alert'), message))
