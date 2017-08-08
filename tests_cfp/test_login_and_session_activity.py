import json

import pytest

# Apparently unused but loading has crucial side effects
import configure

from accuconf import app

from models.user import User

from test_utils.constants import login_menu_item, register_menu_item
# PyCharm fails to spot the use of this symbol as a fixture.
from test_utils.fixtures import client
from test_utils.functions import get_and_check_content, post_and_check_content

from accuconf_cfp.utils import hash_passphrase


@pytest.fixture
def registrant():
    return {
        'email': 'a@b.c',
        'passphrase': 'Passphrase for this user.',
        'name': 'User Name',
        'phone': '+011234567890',
        'country': 'India',
        'state': 'TamilNadu',
        'postal_code': '123456',
        'town_city': 'Chennai',
        'street_address': 'Chepauk',
    }


def test_attempt_to_get_login_page_outside_open_period_causes_redirect(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/login',
                          code=302,
                          includes=('Redirect', '<a href="/">'),
                          )


def test_user_can_register(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 0
    post_and_check_content(client, '/register', json.dumps(registrant), 'application/json',
                           includes=('register_success',),
                           excludes=(login_menu_item, register_menu_item,),
                           )
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 1
    assert user[0].email == registrant['email']
    assert user[0].passphrase == hash_passphrase(registrant['passphrase'])


def test_cannot_login_using_form_submission(client, registrant, monkeypatch):
    test_user_can_register(client, registrant, monkeypatch)
    post_and_check_content(client, '/login',
                           {'email': registrant['email'], 'passphrase': registrant['passphrase']},
                           code=400,
                           includes=('No JSON data returned.',),
                           excludes=(),
                           )


def test_successful_login(client, registrant, monkeypatch):
    test_user_can_register(client, registrant, monkeypatch)
    post_and_check_content(client, '/login',
                           json.dumps({'email': registrant['email'], 'passphrase': registrant['passphrase']}), 'application/json',
                           includes=('login_success',),
                           excludes=(),
                           )


def test_wrong_passphrase_causes_login_failure(client, registrant, monkeypatch):
    test_user_can_register(client, registrant, monkeypatch)
    post_and_check_content(client, '/login',
                           json.dumps({'email': registrant['email'], 'passphrase': 'Passphrase2'}), 'application/json',
                           code=400,
                           includes=('User/passphrase not recognised.',),
                           excludes=(),
                           )


def test_update_user_name(client, registrant, monkeypatch):
    test_successful_login(client, registrant, monkeypatch)
    registrant['name'] = 'Some Dude'
    post_and_check_content(client, '/registration_update', json.dumps(registrant), 'application/json',
                           includes=('registration_update_success',),
                           excludes=(login_menu_item, register_menu_item,),
                           )


def test_logout_without_login_is_noop(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/logout',
                          code=302,
                          includes=('Redirecting', '<a href="/">'),
                          )


def test_logged_in_user_can_logout_with_get(client, registrant, monkeypatch):
    test_successful_login(client, registrant, monkeypatch)
    get_and_check_content(client, '/logout',
                          code=302,
                          includes=('Redirecting', '<a href="/">'),
                          )


def test_logged_in_user_cannot_logout_with_form_post(client, registrant, monkeypatch):
    test_successful_login(client, registrant, monkeypatch)
    post_and_check_content(client, '/logout', registrant,
                           code=405,
                           includes=('Method Not Allowed',),
                           )


def test_logged_in_user_cannot_logout_with_json_post(client, registrant, monkeypatch):
    test_successful_login(client, registrant, monkeypatch)
    post_and_check_content(client, '/logout', json.dumps(registrant), 'application/json',
                           code=405,
                           includes=('Method Not Allowed',),
                           )
