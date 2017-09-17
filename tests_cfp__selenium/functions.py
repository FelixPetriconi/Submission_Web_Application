from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ecs

from server_configuration import base_url
from constants import driver_wait_time


def check_menu_items(driver, expected):
    menu = driver.find_element_by_id('navigation-links').text
    for item in expected:
        assert item in menu


def check_no_menu_items(driver):
    assert not driver.find_element_by_id('navigation-links').text


registered_users = set()


def register_user(driver, registrant):
    identity = hash((driver, registrant['email']))
    if identity not in registered_users:
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
        registered_users.add(identity)


logged_in_users = set()


def login_user(driver, registrant):
    identity = hash((driver, registrant['email']))
    if identity not in logged_in_users:
        driver.get(base_url + 'login')
        wait = WebDriverWait(driver, driver_wait_time)
        wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login'))
        driver.find_element_by_id('email').send_keys(registrant['email'])
        driver.find_element_by_id('passphrase').send_keys(registrant['passphrase'])
        button = wait.until(ecs.element_to_be_clickable((By.ID, 'login')))
        assert 'Login' == button.text
        assert 'loginUser()' == button.get_attribute('onclick')
        button.click()
        wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login Successful'))
        logged_in_users.add(identity)


def register_and_login_user(driver, registrant):
    register_user(driver, registrant)
    login_user(driver, registrant)


def logout_user(driver, registrant):
    driver.get(base_url + 'logout')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Call for Proposals'))
    logged_in_users.remove(hash((driver, registrant['email'])))
