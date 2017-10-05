from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as ecs

import sys
import pathlib
sys.path.insert(0, pathlib.Path(__file__).parent.parent.as_posix())

from server_configuration import base_url
from constants import driver_wait_time

# Apparently unused but has required side effects.
import configure

# NB PyCharm can't tell these are used as fixtures, but they are.
# NB server is a session scope autouse fixture that no test needs direct access to.
from fixtures import driver, server
from test_utils.fixtures import registrant, proposal_single_presenter, proposal_multiple_presenters_single_lead

from functions import register_user, login_user, logout_user
from common_functions import amend_phone, submit_proposal, amend_proposal_one


def test_issue_52_amend_proposal_after_phone_change(driver, registrant, proposal_single_presenter):
    # Register, login, submit a proposal, change phone_number, logout, login, amend proposal
    register_user(driver, registrant)
    login_user(driver, registrant)
    submit_proposal(driver, proposal_single_presenter)
    new_phone = '+44 121 555 6666'
    amend_phone(driver, registrant, new_phone)
    logout_user(driver, registrant)
    registrant['phone'] = new_phone
    login_user(driver, registrant)
    amend_proposal_one(driver)


def test_issue_52_add_proposal_after_phone_change(driver, registrant, proposal_multiple_presenters_single_lead):
    # Register, login, submit a proposal, change password, logout, login, submit new proposal
    #
    # Tests in a module are a stateful sequence so at this point the user is logged in
    # with the new password having successfully amended the first proposal.
    submit_proposal(driver, proposal_multiple_presenters_single_lead)
