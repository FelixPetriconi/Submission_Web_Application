"""
Tests for various uses of the /register route.
"""

import json

# Apparently unused but loading has crucial side effects.
import configure

from accuconf_cfp import app
from accuconf_cfp.utils import hash_passphrase

from models.user import User

# PyCharm fails to spot the use of this symbol as a fixture.
from fixtures import registrant

from test_utils.constants import login_menu_item, register_menu_item
# PyCharm fails to spot this is used as a fixture.
from test_utils.fixtures import client
from test_utils.functions import get_and_check_content, post_and_check_content


def test_attempt_to_get_registration_page_outside_open_period_causes_redirect(client):
    get_and_check_content(client, '/register',
                          code=302,
                          includes=('Redirect', '<a href="/">'),
                          )


def test_registration_page_has_some_countries(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/register',
                          includes=('Register', 'United Kingdom'),
                          excludes=(register_menu_item, 'GBR'),
                          )


def test_attempted_form_submit_not_json_fails(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 0
    post_and_check_content(client, '/register', registrant,
                           code=400,
                           includes=('No JSON data returned',),
                           )
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 0


def test_successful_user_registration(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 0
    post_and_check_content(client, '/register', json.dumps(registrant), 'application/json',
                           includes=('register_success',),
                           excludes=(login_menu_item, register_menu_item,),
                           )
    get_and_check_content(client, '/register_success',
                          includes=(' – Registration Successful', 'You have successfully registered'),
                          excludes=(),
                          )
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 1
    assert user[0].email == registrant['email']
    assert user[0].passphrase == hash_passphrase(registrant['passphrase'])


def test_attempted_duplicate_user_registration_fails(client, registrant, monkeypatch):
    test_successful_user_registration(client, registrant, monkeypatch)
    post_and_check_content(client, '/register', json.dumps(registrant), 'application/json',
                           code=400,
                           includes=('The email address is already in use.',),
                           )


def test_no_passphrase(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    registrant['passphrase'] = ''
    post_and_check_content(client, '/register', json.dumps(registrant), 'application/json',
                           code=400,
                           includes=('No passphrase for new registration.',),
                           )


def test_invalid_email(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    registrant['email'] = 'thing.flob.adob'
    post_and_check_content(client, '/register', json.dumps(registrant), 'application/json',
                           code=400,
                           includes=('Validation failed for the following keys:', 'email'),
                           )


def test_attempt_get_register_success_out_of_open_causes_redirect(client):
    get_and_check_content(client, '/register_success',
                          code=302,
                          includes=('Redirecting', '<a href="/">'),
                          )


def test_attempt_get_registration_update_success_out_of_open_causes_redirect(client):
    get_and_check_content(client, '/registration_update_success',
                          code=302,
                          includes=('Redirecting', '<a href="/">'),
                          excludes=(),
                          )


def test_attempt_to_get_registration_update_success_not_after_registration_update_causes_redirect(client, registrant, monkeypatch):
    test_successful_user_registration(client, registrant, monkeypatch)
    get_and_check_content(client, '/registration_update_success',
                          code=302,
                          includes=('Redirecting', '<a href="/">'),
                          excludes=(),
                          )


def test_attempted_registration_update_not_logged_in(client, registrant, monkeypatch):
    test_successful_user_registration(client, registrant, monkeypatch)
    monkeypatch.setitem(registrant, 'name', 'Jo Bloggs')
    post_and_check_content(client, '/registration_update', json.dumps(registrant), 'application/json',
                           code=302,
                           includes=('Redirecting', '<a href="/">'),
                           excludes=(),
                           )
