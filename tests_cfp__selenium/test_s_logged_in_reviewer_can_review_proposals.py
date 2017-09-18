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

from functions import register_user, register_and_login_user, logout_user


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


def register_a_reviewer(driver, reviewer):
    response = driver.request('POST', base_url + 'register_reviewer', json=reviewer)
    assert response.status_code == 200


def test_logged_in_non_reviewer_cannot_review(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'review_list')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Review List Failed'))
    logout_user(driver, registrant)


def test_logged_in_reviewer_can_review(driver, reviewer):
    register_a_reviewer(driver, reviewer)
    driver.get(base_url + 'review_list')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Review List'))
