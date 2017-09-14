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
from test_utils.fixtures import registrant, proposal_single_presenter, proposal_multiple_presenters_single_lead

user_is_logged_in = False


def register_and_login_user(driver, registrant):
    global user_is_logged_in
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
        driver.get(base_url + 'login')
        wait = WebDriverWait(driver, driver_wait_time)
        wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login'))
        driver.find_element_by_id('email').send_keys(registrant['email'])
        driver.find_element_by_id('passphrase').send_keys(registrant['passphrase'])
        button = wait.until(ecs.element_to_be_clickable((By.ID, 'login')))
        button.click()
        wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Login Successful'))
        user_is_logged_in = True


def test_can_amend_registration_record(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'registration_update')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration Details Updating'))
    assert 'India' == Select(driver.find_element_by_id('country')).first_selected_option.text
    driver.find_element_by_id('name').send_keys('Jo Bloggs')
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    assert 'Save' == driver.find_element_by_id('submit').text
    assert 'registerUser(false)' == button.get_attribute('onclick')
    button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration Update Successful'))
    assert 'Your registration details were successfully updated.' in driver.find_element_by_id('content').text


def test_sees_no_proposal_prior_to_submitting_one(driver, registrant):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'my_proposals')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – My Proposals'))
    element = driver.find_element_by_class_name('first')
    assert 'The following are your current proposals.' in element.text
    proposal_list = driver.find_elements_by_class_name('proposal-list')
    assert len(proposal_list) == 0


def test_can_submit_a_single_presenter_proposal(driver, registrant, proposal_single_presenter):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'submit')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Submit'))
    driver.find_element_by_id('title').send_keys(proposal_single_presenter['title'])
    Select(driver.find_element_by_id('session_type')).select_by_value(proposal_single_presenter['session_type'])
    driver.find_element_by_id('summary').send_keys(proposal_single_presenter['summary'])
    Select(driver.find_element_by_id('audience')).select_by_value(proposal_single_presenter['audience'])
    # driver.find_element_by_id('category').send_keys(proposal_single_presenter['category'])
    driver.find_element_by_id('notes').send_keys(proposal_single_presenter['notes'])
    driver.find_element_by_id('constraints').send_keys(proposal_single_presenter['constraints'])
    presenter = proposal_single_presenter['presenters'][0]
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
    assert 'Submit' == driver.find_element_by_id('submit').text
    assert 'submitProposal()' == button.get_attribute('onclick')
    button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Submission Successful'))
    assert 'Thank you, you have successfully submitted a proposal for the ACCU' in driver.find_element_by_id('content').text


def test_can_submit_a_multiple_presenter_single_lead_proposal(driver, registrant, proposal_multiple_presenters_single_lead):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'submit')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Submit'))
    driver.find_element_by_id('title').send_keys(proposal_multiple_presenters_single_lead['title'])
    Select(driver.find_element_by_id('session_type')).select_by_value(proposal_multiple_presenters_single_lead['session_type'])
    driver.find_element_by_id('summary').send_keys(proposal_multiple_presenters_single_lead['summary'])
    presenter = proposal_multiple_presenters_single_lead['presenters'][0]
    for key in presenter.keys():
        if key == 'is_lead':
            if presenter[key]:
                selected = driver.find_element_by_id(key + '_0_field').is_selected()
                if (presenter[key] and not selected) or (not presenter[key] and selected):
                    driver.find_element_by_id(key + '_0_field').click()
        elif key == 'country':
            Select(driver.find_element_by_id(key + '_0_field')).select_by_value(presenter[key])
        else:
            element = driver.find_element_by_id(key + '_0_field')
            element.clear()
            element.send_keys(presenter[key])
    add_presenter_button = wait.until(ecs.element_to_be_clickable((By.ID, 'add_presenter')))
    assert 'Add Presenter' == driver.find_element_by_id('add_presenter').text
    add_presenter_button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'modal-title'), 'Add Presenter'))
    presenter = proposal_multiple_presenters_single_lead['presenters'][1]
    for key in presenter.keys():
        if key == 'is_lead':
            if presenter[key]:
                selected = driver.find_element_by_id('add-presenter-' + key).is_selected()
                if (presenter[key] and not selected) or (not presenter[key] and selected):
                    driver.find_element_by_id('add-presenter-' + key).click()
        elif key == 'country':
            Select(driver.find_element_by_id('add-presenter-' + key)).select_by_value(presenter[key])
        else:
            element = driver.find_element_by_id('add-presenter-' + key)
            element.clear()
            element.send_keys(presenter[key])
    add_new_presenter_button = wait.until(ecs.element_to_be_clickable((By.ID, 'add_new_presenter')))
    assert 'Add' == driver.find_element_by_id('add_new_presenter').text
    assert 'addNewPresenter()' == add_new_presenter_button.get_attribute('onclick')
    add_new_presenter_button.click()
    submit_button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    assert 'Submit' == driver.find_element_by_id('submit').text
    assert 'submitProposal()' == submit_button.get_attribute('onclick')
    submit_button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Submission Successful'))
    assert 'Thank you, you have successfully submitted a proposal for the ACCU' in driver.find_element_by_id('content').text


def test_can_see_both_previously_submitted_proposals(driver, registrant, proposal_single_presenter, proposal_multiple_presenters_single_lead):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'my_proposals')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – My Proposals'))
    element = driver.find_element_by_class_name('first')
    assert 'The following are your current proposals.' in element.text
    proposal_list = driver.find_elements_by_class_name('proposal-list')
    assert len(proposal_list) == 2
    assert proposal_single_presenter['title'] == proposal_list[0].text
    assert proposal_multiple_presenters_single_lead['title'] == proposal_list[1].text


def test_can_amend_the_first_submitted_proposal(driver, registrant, proposal_single_presenter):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'proposal_update/1')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Update a proposal'))
    title_element = driver.find_element_by_id('title')
    assert proposal_single_presenter['title'] == title_element.get_attribute('value')
    assert '' == title_element.text
    assert proposal_single_presenter['summary'] == driver.find_element_by_id('summary').text
    assert proposal_single_presenter['session_type'] == Select(driver.find_element_by_id('session_type')).first_selected_option.get_attribute('value')
    assert proposal_single_presenter['audience'] == Select(driver.find_element_by_id('audience')).first_selected_option.get_attribute('value')
    assert proposal_single_presenter['notes'] == driver.find_element_by_id('notes').text
    assert proposal_single_presenter['constraints'] == driver.find_element_by_id('constraints').text
    # assert proposal_single_presenter['category'] == driver.find_element_by_id('category').get_attribute('value')
    new_title = 'This is a new title for a proposal'
    title_element.clear()
    title_element.send_keys(new_title)
    assert new_title == title_element.get_attribute('value')
    assert '' == title_element.text
    name_field = driver.find_element_by_id('name_0_field')
    assert proposal_single_presenter['presenters'][0]['name'] == name_field.get_attribute('value')
    assert '' == name_field.text
    new_presenter_name = 'Monty the Gerbil'
    name_field.clear()
    name_field.send_keys(new_presenter_name)
    assert new_presenter_name == name_field.get_attribute('value')
    assert '' == name_field.text
    submit_button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    assert 'Update' == driver.find_element_by_id('submit').text
    assert 'submitProposal(1)' == submit_button.get_attribute('onclick')
    submit_button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal Update Successful'))
    assert 'you have successfully updated your proposal for the ACCU' in driver.find_element_by_id('content').text


def XXX_test_can_amend_the_second_submitted_proposal(driver, registrant, proposal_multiple_presenters_single_lead):
    register_and_login_user(driver, registrant)
    driver.get(base_url + 'proposal_update/2')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Update a proposal'))
    assert proposal_multiple_presenters_single_lead['session_type'] == Select(driver.find_element_by_id('session_type')).first_selected_option.get_attribute('value')
    assert proposal_multiple_presenters_single_lead['audience'] == Select(driver.find_element_by_id('audience')).first_selected_option.get_attribute('value')
    assert proposal_multiple_presenters_single_lead['category'] == driver.find_element_by_id('category').text
    assert proposal_multiple_presenters_single_lead['summary'] == driver.find_element_by_id('summary').text
    title_element = driver.find_element_by_id('title')
    assert proposal_multiple_presenters_single_lead['title'] == title_element.get_attribute('value')
    assert '' == title_element.text
    new_title = 'This is a new title for a proposal'
    title_element.clear()
    title_element.send_keys(new_title)
    assert new_title == title_element.get_attribute('value')
    assert '' == title_element.text
    name_field = driver.find_element_by_id('name_1_field')
    assert proposal_single_presenter['presenters'][1]['name'] == name_field.get_attribute('value')
    assert '' == name_field.text
    new_presenter_name = 'Monty the Gerbil'
    name_field.clear()
    name_field.send_keys(new_presenter_name)
    assert new_presenter_name == name_field.get_attribute('value')
    assert '' == name_field.text
    submit_button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    assert 'Update' == driver.find_element_by_id('submit').text
    assert 'submitProposal(1)' == submit_button.get_attribute('onclick')
    submit_button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Proposal Update Successful'))
    assert 'you have successfully updated your proposal for the ACCU' in driver.find_element_by_id('content').text
