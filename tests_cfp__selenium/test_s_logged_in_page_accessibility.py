import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ecs

from configuration import base_url
from functions import check_menu_items

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

user_is_registered = False


def register_and_login_user(driver, registrant):
    if not user_is_registered:
        driver.get(base_url + 'register')
        wait = WebDriverWait(driver, 4)
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
    driver.get(base_url + 'login')
    wait = WebDriverWait(driver, 4)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login'))
    driver.find_element_by_id('email').send_keys(registrant['email'])
    driver.find_element_by_id('passphrase').send_keys(registrant['passphrase'])
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'login')))
    button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), 'Login Successful'))


def test_logged_in_user_can_get_root_page(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url)
    # assert 'Call for Proposals' in driver.find_element_by_tag_name('title').text
    assert ' – Call for Proposals' in driver.find_element_by_class_name('pagetitle').text
    check_menu_items(driver, ())


def test_logged_in_user_cannot_get_register_page(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'register')
    # assert 'Call for Proposals' in driver.find_element_by_tag_name('title').text
    assert ' – Call for Proposals' in driver.find_element_by_class_name('pagetitle').text
    check_menu_items(driver, ())


def test_logged_in_user_cannot_access_register_success_even_after_logged_in(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'register_success')
    # assert 'Call for Proposals' in driver.find_element_by_tag_name('title').text
    assert ' – Call for Proposals' in driver.find_element_by_class_name('pagetitle').text
    check_menu_items(driver, ())


def test_logged_in_user_can_get_registration_update_page(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'registration_update')
    # assert 'Registration Details Updating' in driver.find_element_by_tag_name('title').text
    assert ' – Registration Details Updating' in driver.find_element_by_class_name('pagetitle').text
    check_menu_items(driver, ())


def test_logged_in_user_cannot_access_registration_update_success_page_logged_in(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'registration_update_success')
    # assert 'Call for Proposals' in driver.find_element_by_tag_name('title').text
    assert ' – Call for Proposals' in driver.find_element_by_class_name('pagetitle').text
    check_menu_items(driver, ())


def test_logged_in_user_cannot_get_login_page(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'login')
    # assert 'Call for Proposals' in driver.find_element_by_tag_name('title').text
    assert ' – Call for Proposals' in driver.find_element_by_class_name('pagetitle').text
    check_menu_items(driver, ())


def test_logged_in_user_cannot_access_login_success_page(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'login_success')
    # assert 'Call for Proposals' in driver.find_element_by_tag_name('title').text
    assert ' – Call for Proposals' in driver.find_element_by_class_name('pagetitle').text
    check_menu_items(driver, ())


def test_logged_in_user_can_get_logout_page(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'logout')
    # assert 'Call for Proposals' in driver.find_element_by_tag_name('title').text
    assert ' – Call for Proposals' in driver.find_element_by_class_name('pagetitle').text
    check_menu_items(driver, ('Register', 'Login'))


def test_logged_in_user_can_get_submit_page(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'submit')
    # assert 'Submit a proposal for ACCU' in driver.find_element_by_tag_name('title').text
    assert ' – Submit a proposal for ACCU' in driver.find_element_by_class_name('pagetitle').text
    check_menu_items(driver, ())


def test_logged_in_user_can_get_my_proposals_page(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'my_proposals')
    # assert 'My Proposals' in driver.find_element_by_tag_name('title').text
    assert ' – My Proposals' in driver.find_element_by_class_name('pagetitle').text
    check_menu_items(driver, ())
