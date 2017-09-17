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

from functions import register_and_login_user

from accuconf_cfp import db
from models.user import User
from models.role_types import Role


def make_this_user_a_reviewer(registrant):
    user = User.query.filter_by(email=registrant['email']).first()
    assert user
    user.role = Role.reviewer
    db.session.commit()
    user = User.query.filter_by(email=registrant['email']).first()
    assert user
    assert user.role == Role.reviewer
