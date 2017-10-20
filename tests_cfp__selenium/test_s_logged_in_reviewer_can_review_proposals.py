import time

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


typed_score = '7'
typed_comment = 'An OK proposal but…'


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
    driver.find_element_by_id('score').send_keys(typed_score)
    driver.find_element_by_id('comment').send_keys(typed_comment)
    submit_button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    assert 'Submit' == submit_button.text
    assert 'submitScoreAndComment(1)' == submit_button.get_attribute('onclick')
    submit_button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    assert 'Review stored.' == driver.find_element_by_id('alert').text
    assert typed_score == driver.find_element_by_id('score').get_attribute('value')
    assert typed_comment == driver.find_element_by_id('comment').get_attribute('value')
    logout_user(driver, reviewer)


def test_logged_in_reviewer_can_move_to_next_proposal(driver, registrant, proposal_multiple_presenters_single_lead, reviewer):
    register_user(driver, registrant)
    submit_a_proposal(driver, registrant, proposal_multiple_presenters_single_lead)
    login_user(driver, reviewer)
    driver.get(base_url + 'review_proposal/1')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    next_button = wait.until(ecs.element_to_be_clickable((By.ID, 'review-next')))
    assert 'Next' == next_button.text
    assert 'navigateNext(1)' == next_button.get_attribute('onclick')
    next_button.click()
    # Travis-CI requires an extra wait here for some reason.
    time.sleep(1)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    assert base_url + 'review_proposal/2' == driver.current_url


def test_logged_in_reviewer_can_move_to_next_unscored_proposal(driver):
    driver.get(base_url + 'review_proposal/1')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    next_button = wait.until(ecs.element_to_be_clickable((By.ID, 'review-next-unscored')))
    assert 'Next Unscored' == next_button.text
    assert 'navigateNextUnscored(1)' == next_button.get_attribute('onclick')
    next_button.click()
    # Travis-CI requires an extra wait here for some reason.
    time.sleep(1)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    assert base_url + 'review_proposal/2' == driver.current_url


def test_logged_in_reviewer_can_move_to_previous_proposal(driver):
    driver.get(base_url + 'review_proposal/2')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    previous_button = wait.until(ecs.element_to_be_clickable((By.ID, 'review-previous')))
    assert 'Previous' == previous_button.text
    assert 'navigatePrevious(2)' == previous_button.get_attribute('onclick')
    previous_button.click()
    # Travis-CI requires an extra wait here for some reason.
    time.sleep(1)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    assert base_url + 'review_proposal/1' == driver.current_url
    # This is a scored proposal so make sure the scores are present.
    assert typed_score == driver.find_element_by_id('score').get_attribute('value')
    assert typed_comment == driver.find_element_by_id('comment').text


def test_logged_in_reviewer_cannot_move_to_previous_unscored_proposal_if_they_have_reviewed_them_all(driver):
    driver.get(base_url + 'review_proposal/2')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    previous_button = wait.until(ecs.element_to_be_clickable((By.ID, 'review-previous-unscored')))
    assert 'Previous Unscored' == previous_button.text
    assert 'navigatePreviousUnscored(2)' == previous_button.get_attribute('onclick')
    # TODO Why can't the alert be detected
    # previous_button.click()
    # wait.until(ecs.alert_is_present())
    # alert = driver.switch_to_alert()
    # assert 'Requested proposal does not exist.' == alert.text
    # alert.accept()
    assert base_url + 'review_proposal/2' == driver.current_url


def test_amending_a_score_doesnt_create_a_second_score_object(driver):
    driver.get(base_url + 'review_proposal/1')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    new_score = '8'
    new_comment = 'A different comment.'
    score_node = driver.find_element_by_id('score')
    score_node.clear()
    score_node.send_keys(new_score)
    comment_node = driver.find_element_by_id('comment')
    comment_node.clear()
    comment_node.send_keys(new_comment)
    submit_button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    assert 'Update' == submit_button.text
    assert 'submitScoreAndComment(1)' == submit_button.get_attribute('onclick')
    submit_button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    assert 'Review stored.' == driver.find_element_by_id('alert').text
    assert new_score == driver.find_element_by_id('score').get_attribute('value')
    assert new_comment == driver.find_element_by_id('comment').get_attribute('value')
    next_button = wait.until(ecs.element_to_be_clickable((By.ID, 'review-next')))
    assert 'Next' == next_button.text
    assert 'navigateNext(1)' == next_button.get_attribute('onclick')
    next_button.click()
    # Travis-CI requires an extra wait here for some reason.
    time.sleep(2)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    previous_button = wait.until(ecs.element_to_be_clickable((By.ID, 'review-previous')))
    assert 'Previous' == previous_button.text
    assert 'navigatePrevious(2)' == previous_button.get_attribute('onclick')
    previous_button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal to Review'))
    assert base_url + 'review_proposal/1' == driver.current_url
    assert new_score == driver.find_element_by_id('score').get_attribute('value')
    assert new_comment == driver.find_element_by_id('comment').text
