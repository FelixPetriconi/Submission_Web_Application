import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ecs

from configuration import base_url
from constants import driver_wait_time

# NB PyCharm can't tell these are used as fixtures, but they are.
# NB server is an session scope autouse fixture that no test needs direct access to.
from fixtures import driver, server, registrant

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
    assert 'Your registration details were successful updated.' in driver.find_element_by_id('content').text


@pytest.fixture
def proposal_single_presenter():
    return {
        'title': 'ACCU Proposal',
        'session_type': 'quickie',
        'summary': '''This is a test proposal that will have
dummy data. Also this is not a very
lengthy proposal''',
        'presenters': [
            {
                'email': 'a@b.c',
                'name': 'User Name',
                'is_lead': True,
                'bio': 'A nice member of the human race.',
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
    driver.find_element_by_id('session_type').send_keys(proposal_single_presenter['session_type'])
    driver.find_element_by_id('summary').send_keys(proposal_single_presenter['summary'])
    presenter = proposal_single_presenter['presenters'][0]
    driver.find_element_by_class_name('email_field').send_keys(presenter['email'])
    driver.find_element_by_class_name('name_field').send_keys(presenter['name'])
    driver.find_element_by_class_name('bio_field').send_keys(presenter['bio'])
    driver.find_element_by_class_name('country_field').send_keys(presenter['country'])
    driver.find_element_by_class_name('state_field').send_keys(presenter['state'])
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    assert 'Submit' == driver.find_element_by_id('submit').text
    assert 'submitProposal()' == button.get_attribute('onclick')
    button.click()
    wait.until(ecs.presence_of_element_located((By.CLASS_NAME, 'pagetitle')))
    print(driver.find_element_by_class_name('pagetitle').text)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), 'Submission Successful'))
    assert 'Thank you, you have successfully submitted a proposal for the ACCU' in driver.find_element_by_id('content').text
