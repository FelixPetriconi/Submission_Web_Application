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

new_passphrase = 'squirrels having a bundle'


def register_user(driver, registrant):
    driver.get(base_url + 'register')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Register'))
    for key, value in registrant.items():
        driver.find_element_by_id(key).send_keys(value)
    puzzle_text = driver.find_element_by_id('puzzle_label').text
    driver.find_element_by_id('puzzle').send_keys(eval(puzzle_text))
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration Successful'))


def login_user(driver, registrant, passphrase):
    driver.get(base_url + 'login')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login'))
    driver.find_element_by_id('email').send_keys(registrant['email'])
    driver.find_element_by_id('passphrase').send_keys(passphrase)
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'login')))
    button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login Successful'))


def logout_user(driver):
    driver.get(base_url + 'logout')
    WebDriverWait(driver, driver_wait_time).until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Call for Proposals'))


def amend_passphrase(driver, registrant):
    driver.get(base_url + 'registration_update')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration Details Updating'))
    driver.find_element_by_id('passphrase').send_keys(new_passphrase)
    driver.find_element_by_id('cpassphrase').send_keys(new_passphrase)
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration Update Successful'))


def submit_proposal(driver, proposal):
    driver.get(base_url + 'submit')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Submit'))
    driver.find_element_by_id('title').send_keys(proposal['title'])
    Select(driver.find_element_by_id('session_type')).select_by_value(proposal['session_type'])
    driver.find_element_by_id('summary').send_keys(proposal['summary'])
    try:
        Select(driver.find_element_by_id('audience')).select_by_value(proposal['audience'])
    except KeyError:
        pass
    # driver.find_element_by_id('category').send_keys(proposal['category'])
    try:
        driver.find_element_by_id('notes').send_keys(proposal['notes'])
    except KeyError:
        pass
    try:
        driver.find_element_by_id('constraints').send_keys(proposal['constraints'])
    except KeyError:
        pass
    presenter = proposal['presenters'][0]
    for key in presenter.keys():
        if key == 'is_lead':
            selected = driver.find_element_by_id(key + '_0_field').is_selected()
            if (presenter[key] and not selected) or (not presenter[key] and selected):
                driver.find_element_by_id(key + '_0_field').click()
        elif key == 'country':
            Select(driver.find_element_by_id(key + '_0_field')).select_by_value(presenter[key])
        else:
            element = driver.find_element_by_id(key + '_0_field')
            element.clear()
            element.send_keys(presenter[key])
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Submission Successful'))


def amend_proposal_one(driver):
    driver.get(base_url + 'proposal_update/1')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Update a proposal'))
    title_element = driver.find_element_by_id('title')
    new_title = 'This is a new title for a proposal'
    title_element.clear()
    title_element.send_keys(new_title)
    name_field = driver.find_element_by_id('name_0_field')
    new_presenter_name = 'Monty the Gerbil'
    name_field.clear()
    name_field.send_keys(new_presenter_name)
    submit_button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    submit_button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal Update Successful'))


def test_issue_52_amend_proposal_after_password_change(driver, registrant, proposal_single_presenter):
    # Register, login, submit a proposal, change password, logout, login, amend proposal
    register_user(driver, registrant)
    login_user(driver, registrant, registrant['passphrase'])
    submit_proposal(driver, proposal_single_presenter)
    amend_passphrase(driver, registrant)
    logout_user(driver)
    login_user(driver, registrant, new_passphrase)
    amend_proposal_one(driver)


def test_issue_52_add_proposal_after_password_change(driver, registrant, proposal_multiple_presenters_single_lead):
    # Register, login, submit a proposal, change password, logout, login, submit new proposal
    #
    # Tests in a module are a stateful sequence so at this point the user is logged in
    # with the new password having successfully amended the first proposal.
    submit_proposal(driver, proposal_multiple_presenters_single_lead)
