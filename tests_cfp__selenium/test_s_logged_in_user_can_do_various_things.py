import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as ecs

from server_configuration import base_url
from constants import driver_wait_time

# Apparently unused but has required side effects.
import configure

# NB PyCharm can't tell these are used as fixtures, but they are.
# NB server is an session scope autouse fixture that no test needs direct access to.
from fixtures import driver, server
from test_utils.fixtures import registrant

user_is_logged_in = False


def register_and_login_user(driver, registrant):
    if not user_is_logged_in:
        driver.get(base_url + 'register')
        wait = WebDriverWait(driver, driver_wait_time)
        wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Register'))
        for key, value in registrant.items():
            driver.find_element_by_id(key).send_keys(value)
        puzzle_text = driver.find_element_by_id('puzzle_label').text
        driver.find_element_by_id('puzzle').send_keys(eval(puzzle_text))
        button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
        assert 'Register' in button.text
        assert 'registerUser(true)' in button.get_attribute('onclick')
        button.click()
        wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration Successful'))
        assert 'You have successfully registered for submitting proposals for the ACCU' in driver.find_element_by_id('content').text
        global user_is_logged_in
        user_is_logged_in = True
        driver.get(base_url + 'login')
        wait = WebDriverWait(driver, driver_wait_time)
        wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login'))
        driver.find_element_by_id('email').send_keys(registrant['email'])
        driver.find_element_by_id('passphrase').send_keys(registrant['passphrase'])
        button = wait.until(ecs.element_to_be_clickable((By.ID, 'login')))
        button.click()
        wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), 'Login Successful'))


def test_logged_in_user_can_amend_registration_record(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'registration_update')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration Details Updating'))
    driver.find_element_by_id('name').send_keys('Jo Bloggs')
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    assert 'Save' == driver.find_element_by_id('submit').text
    assert 'registerUser(false)' == button.get_attribute('onclick')
    button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), 'Registration Update Successful'))
    assert 'Your registration details were successfully updated.' in driver.find_element_by_id('content').text


@pytest.fixture
def proposal_single_presenter():
    return {
        'title': 'A Proposal for a Quickie',
        'session_type': 'quickie',
        'summary': '''This is a test proposal that will have
dummy data. Also this is not a very
lengthy proposal. But it is longer than the
minimum requirement.''',
        'presenters': [
            {
                'email': 'a@b.c',
                'name': 'User Name',
                'is_lead': True,
                'bio': 'A nice member of the human race who has some experience of presenting.',
                'country': 'India',
                'state': 'TamilNadu'
            },
        ]
    }


def test_logged_in_user_can_submit_a_proposal(driver, registrant, proposal_single_presenter):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'submit')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Submit'))
    driver.find_element_by_id('title').send_keys(proposal_single_presenter['title'])
    Select(driver.find_element_by_id('session_type')).select_by_value(proposal_single_presenter['session_type'])
    driver.find_element_by_id('summary').send_keys(proposal_single_presenter['summary'])
    presenter = proposal_single_presenter['presenters'][0]
    for key in presenter.keys():
        if key == 'is_lead':
            if presenter[key]:
                driver.find_element_by_class_name(key + '_field').click()
        elif key == 'country':
            Select(driver.find_element_by_class_name(key + '_field')).select_by_value(presenter[key])
        else:
            element = driver.find_element_by_class_name(key + '_field')
            element.clear()
            element.send_keys(presenter[key])
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    assert 'Submit' == driver.find_element_by_id('submit').text
    assert 'submitProposal()' == button.get_attribute('onclick')
    button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), 'Submission Successful'))
    assert 'Thank you, you have successfully submitted a proposal for the ACCU' in driver.find_element_by_id('content').text
