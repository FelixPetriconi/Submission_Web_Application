"""
Tests for various uses of the /register route.
"""

import pytest

from common import client, post_and_check_content

from accuconf import app


@pytest.fixture
def registrant():
    return {
        'email': 'a@b.c',
        'passphrase': 'Passphrase1',
        'cpassphrase': 'Passphrase1',
        'name': 'User Name',
        'phone': '+011234567890',
        'country': 'India',
        'state': 'TamilNadu',
        'postalcode': '123456',
        'towncity' : 'Chennai',
        'streetaddress': 'Chepauk',
        'captcha': '1',
        'question': '12',
    }


def test_successful_user_registration(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    post_and_check_content(client, '/register', registrant, includes=('You have successfully registered', 'Please login'))


def test_attempted_duplicate_user_registration_fails(client, registrant, monkeypatch):
    test_successful_user_registration(client, registrant, monkeypatch)
    post_and_check_content(client, '/register', registrant, includes=('The email address was either invalid or already in use.',))


def test_passphrase_and_cpassphrase_present_but_differ(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    registrant['passphrase'] = 'the lazy dog'
    registrant['cpassphrase'] = 'brown fox'
    post_and_check_content(client, '/register', registrant, includes=('Passphrase and confirmation passphrase dffer.',))


def test_no_passphrase_or_cpassphrase(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    registrant['passphrase'] = ''
    registrant['cpassphrase'] = ''
    post_and_check_content(client, '/register', registrant, includes=('Neither passphrase nor confirmation passphrase entered.',))


def test_passphrase_but_no_cpassphrase(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    registrant['cpassphrase'] = ''
    post_and_check_content(client, '/register', registrant, includes=('Passphrase given but no confirmation passphrase',))


def test_no_passphrase_but_cpassphrase(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    registrant['passphrase'] = ''
    post_and_check_content(client, '/register', registrant, includes=('No passphrase given but even though confirmation passphrase given.',))


def test_invalid_email(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    registrant['email'] = 'thing.flob.adob'
    post_and_check_content(client, '/register', registrant, includes=('The email address was either invalid or already in use',))

