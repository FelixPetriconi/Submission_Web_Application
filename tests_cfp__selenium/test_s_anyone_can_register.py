import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ecs

# Apparently unused but has required side effects.
import configure

from server_configuration import base_url
from constants import driver_wait_time

# NB PyCharm can't tell these are used as fixtures, but they are.
# NB server is a session scope autouse fixture that no test needs direct access to.
from fixtures import driver, server
from test_utils.fixtures import registrant


def submit_data_to_register_page(driver, registrant):
    driver.get(base_url + 'register')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Register'))
    for key, value in registrant.items():
        driver.find_element_by_id(key).send_keys(value)
    puzzle_text = driver.find_element_by_id('puzzle_label').text
    driver.find_element_by_id('puzzle').send_keys(eval(puzzle_text))
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    assert 'Register' == button.text
    assert 'registerUser(true)' == button.get_attribute('onclick')
    button.click()


@pytest.mark.parametrize(('key', 'value', 'message'), (
    ('email', 'a.b.c', 'Email should be of the format user@example.com'),
    ('passphrase', 'hum', 'Passphrase is not valid.'),
    ('cpassphrase', 'dedum', 'Passphrase and confirmation passphrase not the same.'),
    ('name', 'R', 'Invalid name.'),
    ('phone', 'blurb', 'Invalid phone number.'),
    ('postal_code', 'Fubar', 'Invalid postal code.'),
))
def test_single_error_causing_local_failure(key, value, message, driver, registrant, monkeypatch):
    monkeypatch.setitem(registrant, key, value)
    submit_data_to_register_page(driver, registrant)
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Register'))
    assert 'Problem with form, not submitting.' == driver.find_element_by_id('alert').text
    assert message in driver.find_element_by_id(key + '_alert').text


def test_anyone_can_successfully_register(driver, registrant):
    submit_data_to_register_page(driver, registrant)
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration Successful'))
    assert 'You have successfully registered for submitting proposals for the ACCU' in driver.find_element_by_id('content').text
