"""
Tests for various uses of the /register route.
"""

import json

import pytest

# Apparently unused but loading has crucial side effects.
import configure

from accuconf import app

from models.user import User

from test_utils.constants import login_menu_item, register_menu_item
# PyCharm fails to spot this is used as a fixture.
from test_utils.fixtures import client
from test_utils.functions import get_and_check_content, post_and_check_content

from accuconf_cfp.utils import hash_passphrase

# TODO For some reason we have to import the class Score, why?
from models.score import Score


@pytest.fixture
def registrant():
    return {
        'email': 'a@b.c',
        'passphrase': 'Passphrase for someone',
        'name': 'User Name',
        'phone': '+011234567890',
        'country': 'India',
        'state': 'TamilNadu',
        'postal_code': '123456',
        'town_city': 'Chennai',
        'street_address': 'Chepauk',
    }


def test_registration_page_has_some_countries(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/register',
                          includes=('Register', 'United Kingdom'),
                          excludes=(register_menu_item, 'GBR'))


def test_attempted_form_submit_not_json_fails(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 0
    post_and_check_content(client, '/register', registrant,
                           includes=('Registration Failure', 'No JSON data returned', login_menu_item),
                           excludes=(register_menu_item,))
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 0


def test_successful_user_registration(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 0
    post_and_check_content(client, '/register', json.dumps(registrant), 'application/json',
                           includes=('You have successfully registered', 'Please login', login_menu_item),
                           excludes=(register_menu_item,))
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 1
    assert user[0].email == registrant['email']
    assert user[0].passphrase == hash_passphrase(registrant['passphrase'])


def test_attempted_duplicate_user_registration_fails(client, registrant, monkeypatch):
    test_successful_user_registration(client, registrant, monkeypatch)
    post_and_check_content(client, '/register', json.dumps(registrant), 'application/json',
                           includes=('The email address is already in use.', login_menu_item),
                           excludes=(register_menu_item,))


def test_no_passphrase(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    registrant['passphrase'] = ''
    post_and_check_content(client, '/register', json.dumps(registrant), 'application/json',
                           includes=('No passphrase for new registration.', login_menu_item),
                           excludes=(register_menu_item,))


def test_invalid_email(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    registrant['email'] = 'thing.flob.adob'
    post_and_check_content(client, '/register', json.dumps(registrant), 'application/json',
                           includes=('Validation failed for the following keys:', 'email', login_menu_item),
                           excludes=(register_menu_item,))
