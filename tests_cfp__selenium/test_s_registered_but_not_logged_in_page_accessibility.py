import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ecs

from server_configuration import base_url
from functions import check_menu_items
from constants import driver_wait_time

# Apparently unused but has required side effects.
import configure

# NB PyCharm can't tell these are used as fixtures, but they are.
# NB server is an session scope autouse fixture that no test needs direct access to.
from fixtures import driver, server
from test_utils.fixtures import registrant

user_is_registered = False


def register_user(driver, registrant):
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
        global user_is_registered
        user_is_registered = True


def test_can_get_root_page(driver, registrant):
    register_user(driver, registrant)
    driver.get(base_url)
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Call for Proposals'))
    check_menu_items(driver, ('Register', 'Login'))


def test_can_get_register_page(driver, registrant):
    register_user(driver, registrant)
    driver.get(base_url + 'register')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Register'))
    assert 'Register here for submitting proposals to the ACCU' in driver.find_element_by_class_name('first').text
    check_menu_items(driver, ('Login',))


def test_cannot_access_register_success_even_after_registering(driver, registrant):
    register_user(driver, registrant)
    driver.get(base_url + 'register_success')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Call for Proposals'))
    check_menu_items(driver, ('Register', 'Login'))


def test_cannot_get_registration_update_page_not_logged_in(driver, registrant):
    register_user(driver, registrant)
    driver.get(base_url + 'registration_update')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Call for Proposals'))
    check_menu_items(driver, ('Register', 'Login'))


def test_cannot_access_registration_update_success_page_not_logged_in(driver, registrant):
    register_user(driver, registrant)
    driver.get(base_url + 'registration_update_success')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Call for Proposals'))
    check_menu_items(driver, ('Register', 'Login'))


def test_can_get_login_page(driver, registrant):
    register_user(driver, registrant)
    driver.get(base_url + 'login')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login'))
    check_menu_items(driver, ('Register',))


def test_cannot_access_login_success_page_if_not_logged_in(driver, registrant):
    register_user(driver, registrant)
    driver.get(base_url + 'login_success')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Call for Proposals'))
    check_menu_items(driver, ('Register', 'Login'))


def test_can_get_logout_page(driver, registrant):
    register_user(driver, registrant)
    driver.get(base_url + 'logout')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Call for Proposals'))
    check_menu_items(driver, ('Register', 'Login'))


def test_cannot_get_submit_page_if_not_logged_in(driver, registrant):
    register_user(driver, registrant)
    driver.get(base_url + 'submit')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Submit Not Possible'))
    assert 'You must be registered and logged in to submit a proposal.' in driver.find_element_by_class_name('first').text
    check_menu_items(driver, ('Register', 'Login'))


def test_cannot_get_submit_success_page_if_not_logged_in(driver):
    driver.get(base_url + 'submit_success')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Submit Failed'))
    assert 'You must be registered and logged in to submit a proposal.' in driver.find_element_by_class_name('first').text
    check_menu_items(driver, ('Register', 'Login'))


def test_cannot_get_my_proposals_page_unless_logged_in(driver, registrant):
    register_user(driver, registrant)
    driver.get(base_url + 'my_proposals')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – My Proposals Failure'))
    assert 'You must be registered and logged in to discover your current proposals' in driver.find_element_by_class_name('first').text
    check_menu_items(driver, ('Register', 'Login'))
