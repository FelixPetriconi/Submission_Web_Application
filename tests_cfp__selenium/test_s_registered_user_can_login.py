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

user_is_registered = False


def register_user(driver, registrant):
    global user_is_registered
    if not user_is_registered:
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
        wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration Successful'))
        assert 'You have successfully registered for submitting proposals for the ACCU' in driver.find_element_by_id('content').text
        user_is_registered = True


@pytest.mark.parametrize(('email', 'passphrase', 'error_key'), (
    ('', '', 'email'),
    ('russel.winder.org.uk', '', 'email'),
    ('russel@winder.org.uk', '', 'passphrase'),
))
def test_malformed_data_cases_local_error(email, passphrase, error_key, driver):
    driver.get(base_url + 'login')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login'))
    driver.find_element_by_id('email').send_keys(email)
    driver.find_element_by_id('passphrase').send_keys(passphrase)
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'login')))
    button.click()
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login'))
    assert 'Problem with login form, not submitting.' in driver.find_element_by_id('alert').text
    assert 'not valid.' in driver.find_element_by_id(error_key + '_alert').text


def test_user_can_successfully_login(driver, registrant):
    register_user(driver, registrant)
    driver.get(base_url + 'login')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login'))
    driver.find_element_by_id('email').send_keys(registrant['email'])
    driver.find_element_by_id('passphrase').send_keys(registrant['passphrase'])
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'login')))
    button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), 'Login Successful'))


def tests_cannot_get_login_page_when_logged_in(driver, registrant):
    driver.get(base_url + 'login')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Call for Proposals'))


def test_logged_in_user_can_logout(driver):
    driver.get(base_url + 'logout')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Call for Proposals'))
