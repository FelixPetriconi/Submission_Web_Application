import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ecs

from server_configuration import base_url
from constants import driver_wait_time

# Apparently unused but has required side effects.
import configure

# NB PyCharm can't tell these are used as fixtures, but they are.
# NB server is a session scope autouse fixture that no test needs direct access to.
from fixtures import driver, server
from test_utils.fixtures import registrant

from functions import register_user


@pytest.mark.parametrize(('email', 'passphrase', 'error_key', 'error_message'), (
    ('', '', 'email', 'Email not valid.'),
    ('russel.winder.org.uk', '', 'email', 'Email not valid.'),
    ('russel@winder.org.uk', '', 'passphrase', 'Passphrase must be at least 8 characters long.'),
))
def test_malformed_data_cases_local_error(email, passphrase, error_key, error_message, driver):
    driver.get(base_url + 'login')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login'))
    driver.find_element_by_id('email').send_keys(email)
    driver.find_element_by_id('passphrase').send_keys(passphrase)
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'login')))
    button.click()
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login'))
    assert 'Problem with login form, not submitting.' in driver.find_element_by_id('alert').text
    assert driver.find_element_by_id(error_key + '_alert').text == error_message


def test_registered_user_can_successfully_login(driver, registrant):
    register_user(driver, registrant)
    driver.get(base_url + 'login')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login'))
    driver.find_element_by_id('email').send_keys(registrant['email'])
    driver.find_element_by_id('passphrase').send_keys(registrant['passphrase'])
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'login')))
    button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), 'Login Successful'))


#  This test relies on the above test having run successfully in order to set the per module
#  state to registered user logged in.
def tests_cannot_get_login_page_when_logged_in(driver, registrant):
    driver.get(base_url + 'login')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Call for Proposals'))


# This test changes the state of the per module driver and so must be run as the last test in this module.
# By default pytest runs tests in declaration order so this should not be fragile.
def test_logged_in_user_can_logout(driver):
    driver.get(base_url + 'logout')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Call for Proposals'))
