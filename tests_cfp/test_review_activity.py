import json

from flask import session

# Apparently unused but loading has crucial side effects
import configure

from accuconf_cfp import app, db
from accuconf_cfp.utils import hash_passphrase

from models.user import User
from models.role_types import Role

# PyCharm fails to spot the use of this symbol as a fixture.
from fixtures import registrant

from test_utils.constants import login_menu_item, logout_menu_item, my_proposals_menu_item, register_menu_item, registration_update_menu_item, submit_menu_item
# PyCharm fails to spot the use of this symbol as a fixture.
from test_utils.fixtures import client
from test_utils.functions import get_and_check_content, post_and_check_content


def test_attempt_to_get_review_list_page_outside_open_period_causes_redirect(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/review_list',
                          code=302,
                          includes=('Redirect', '<a href="/">'),
                          )


def test_reviewer_can_register_and_login(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 0
    post_and_check_content(client, '/register', json.dumps(registrant), 'application/json',
                           includes=('register_success',),
                           excludes=(),
                           )
    get_and_check_content(client, '/register_success',
                          includes=(' – Registration Successful', 'You have successfully registered', login_menu_item, register_menu_item),
                          excludes=(logout_menu_item, my_proposals_menu_item, registration_update_menu_item, submit_menu_item),
                          )
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 1
    user = user[0]
    assert user.email == registrant['email']
    assert user.passphrase == hash_passphrase(registrant['passphrase'])
    assert user.role == Role.user
    user.role = Role.reviewer
    db.session.commit()
    post_and_check_content(client, '/login',
                           json.dumps({'email': registrant['email'], 'passphrase': registrant['passphrase']}), 'application/json',
                           includes=('login_success',),
                           excludes=(),
                           )
    get_and_check_content(client, '/login_success',
                          includes=(' – Login Successful', 'Login successful', logout_menu_item, my_proposals_menu_item, registration_update_menu_item, submit_menu_item),
                          excludes=(login_menu_item, register_menu_item),
                          )


def XXX_test_logged_in_reviewer_can_get_review_list(client, registrant, monkeypatch):
    test_reviewer_can_register_and_login(client, registrant, monkeypatch)
    get_and_check_content(client, '/review_list',
                          includes=(' – List of Proposals',),
                          excludes=(),
                          )
