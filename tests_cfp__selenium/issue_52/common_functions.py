from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as ecs

from server_configuration import base_url
from constants import driver_wait_time


def amend_passphrase(driver, registrant, new_passphrase):
    driver.get(base_url + 'registration_update')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration Details Updating'))
    driver.find_element_by_id('passphrase').send_keys(new_passphrase)
    driver.find_element_by_id('cpassphrase').send_keys(new_passphrase)
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    button.click()
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration Update Successful'))


def amend_phone(driver, registrant, new_phone):
    driver.get(base_url + 'registration_update')
    wait = WebDriverWait(driver, driver_wait_time)
    wait.until(ecs.text_to_be_present_in_element((By.CLASS_NAME, 'pagetitle'), ' – Registration Details Updating'))
    driver.find_element_by_id('phone').send_keys(new_phone)
    button = wait.until(ecs.element_to_be_clickable((By.ID, 'submit')))
    button.click()
    pagetitle_node = wait.until(ecs.presence_of_element_located((By.CLASS_NAME, 'pagetitle')))
    assert '' == pagetitle_node.text, pagetitle_node.text
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
