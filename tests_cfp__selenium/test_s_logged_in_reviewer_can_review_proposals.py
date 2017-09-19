import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as ecs

from server_configuration import base_url
from constants import driver_wait_time

# Apparently unused but has required side effects.
import configure

# NB PyCharm can't tell these are used as fixtures, but they are.
# NB server is a session scope autouse fixture that no test needs direct access to.
from fixtures import driver, server
from test_utils.fixtures import registrant, proposal_single_presenter, proposal_multiple_presenters_single_lead

from functions import register_user, register_and_login_user, login_user, logout_user


@pytest.fixture
def reviewer():
    return {
        'email': 'x@y.z',
        'passphrase': 'Passphrase for this user.',
        'name': 'Reviewer Name',
        'phone': '+011234567890',
        'country': 'India',
        'state': 'TamilNadu',
        'postal_code': '123456',
        'town_city': 'Chennai',
        'street_address': 'Chepauk',
    }


registered_reviewers = set()


def register_a_reviewer(driver, reviewer):
    id = hash((driver, reviewer['email']))
    if id not in registered_reviewers:
        response = driver.request('POST', base_url + 'register_reviewer', json=reviewer)
        assert response.status_code == 200
        registered_reviewers.add(id)


def submit_a_proposal(driver, proposer, proposal):
    login_user(driver, proposer)
    response = driver.request('POST', base_url + 'submit', json=proposal)
    assert response.status_code == 200
    logout_user(driver, proposer)


def test_logged_in_non_reviewer_cannot_review(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'review_list')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Review List Failed'))
    logout_user(driver, registrant)


def test_not_logged_in_reviewer_cannot_get_review_list(driver, reviewer):
    register_a_reviewer(driver, reviewer)
    driver.get(base_url + 'review_list')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Review List Failed'))


def test_logged_in_reviewer_can_get_review_list(driver, reviewer):
    register_a_reviewer(driver, reviewer)
    login_user(driver, reviewer)
    driver.get(base_url + 'review_list')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – List of Proposals'))
    logout_user(driver, reviewer)


def test_logged_in_reviewer_can_review_submitted_proposal(driver, registrant, proposal_single_presenter, reviewer):
    register_user(driver, registrant)
    submit_a_proposal(driver, registrant, proposal_single_presenter)
    register_a_reviewer(driver, reviewer)
    login_user(driver, reviewer)
    driver.get(base_url + 'review_list')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – List of Proposals'))
    link = wait.until(ecs.element_to_be_clickable((By.LINK_TEXT, proposal_single_presenter['title'])))
    link.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    driver.find_element_by_id('score').send_keys('7')
    driver.find_element_by_id('comment').send_keys('An OK proposal but…')
    submit_button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    assert 'Submit' == submit_button.text
    assert 'submitScoreAndComment(1)' == submit_button.get_attribute('onclick')
    submit_button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    logout_user(driver, reviewer)


# NB There is now a proposer, a submission and a reviewer in the database.
