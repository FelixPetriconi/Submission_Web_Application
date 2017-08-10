import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ecs

from configuration import base_url
from constants import driver_wait_time

# NB PyCharm can't tell these are used as fixtures, but they are.
# NB server is an session scope autouse fixture that no test needs direct access to.
from fixtures import driver, server, registrant

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
        assert 'Register' in button.text
        assert 'registerUser()' in button.get_attribute('onclick')
        button.click()
        wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration Successful'))
        assert 'You have successfully registered for submitting proposals for the ACCU' in driver.find_element_by_id('content').text
        global user_is_registered
        user_is_registered = True


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
