from configuration import base_url

# NB PyCharm can't tell these are used as fixtures, but they are.
# NB server is an session scope autouse fixture that no test needs direct access to.
from fixtures import driver, server

# NB The server is in "call open" state.


def test_can_get_root_page(driver):
    driver.get(base_url)
    assert 'Call for Proposals' in driver.find_element_by_tag_name('title').text
    assert ' – Call for Proposals' in driver.find_element_by_class_name('pagetitle').text


def test_can_get_register_page(driver):
    driver.get(base_url + 'register')
    # assert 'Registration' in driver.find_element_by_tag_name('title').text
    assert ' – Register' in driver.find_element_by_class_name('pagetitle').text
    assert 'Register here for submitting proposals to ACCU Conference' in driver.find_element_by_class_name('first').text


def test_can_access_register_success_page(driver):
    driver.get(base_url + 'register_success')
    # assert 'Registration Successful' in driver.find_element_by_tag_name('title').text
    assert ' – Registration Successful' in driver.find_element_by_class_name('pagetitle').text
    assert 'You have successfully registered' in driver.find_element_by_class_name('first').text


def test_cannot_get_registration_update_page_not_logged_in(driver):
    driver.get(base_url + 'registration_update')
    # assert 'Registration Failure' in driver.find_element_by_tag_name('title').text
    assert ' – Registration Update Failure' in driver.find_element_by_class_name('pagetitle').text
    assert 'You must be logged in to update registration details.' in driver.find_element_by_class_name('first').text


def test_cannot_access_registration_update_success_page_not_logged_in(driver):
    driver.get(base_url + 'registration_update_success')
    # assert 'Registration Failure' in driver.find_element_by_tag_name('title').text
    assert ' – Registration Update Failure' in driver.find_element_by_class_name('pagetitle').text
    assert 'You must be logged in to update registration details.' in driver.find_element_by_class_name('first').text


def test_can_get_login_page(driver):
    driver.get(base_url + 'login')
    # assert 'Login' in driver.find_element_by_tag_name('title').text
    assert ' – Login' in driver.find_element_by_class_name('pagetitle').text
