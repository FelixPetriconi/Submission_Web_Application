import pytest

from flask import session

# Apparently unused but has required side effects.
import configure

from accuconf_cfp import app
import accuconf_cfp.utils as utils


def test_hash_passphrase():
    assert utils.hash_passphrase('Hello World.') == 'fee4e02329c0e1c9005d0590f4773d8e519e0cda859775ac9c83641e3a960c57e7ad461354e4860722b6e3c161e493e04f5ef07d9169ff7bdab659d6a57cc316'


def test_is_acceptable_route_default():
    assert utils.is_acceptable_route()[0]


def test_is_acceptable_route_maintenance(monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    assert not utils.is_acceptable_route()[0]


def test_is_acceptable_route_no_call_no_reviewing(monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    assert not utils.is_acceptable_route()[0]


def test_is_logged_in_default():
    with app.test_request_context('/'):
        assert not utils.is_logged_in()


def test_is_logged_in_forced():
    with app.test_request_context('/'):
        session['email'] = 'russel@winder.org.uk'
        assert utils.is_acceptable_route()[0]


def test_reasonable_email():
    assert utils.is_valid_email('russel@winder.org.uk')


def test_string_with_no_at_is_not_email():
    assert not utils.is_valid_email('russel.winder.org.uk')


def test_passphrase_too_short_less_than_8_characters_fails():
    assert not utils.is_valid_passphrase('xx')


def test_passphrase_long_enough_8_or_more_characters_works():
    assert utils.is_valid_passphrase('xxxxxxxx')


def test_utf8_encoded_unicode_codepoints_are_acceptable_in_passphrases():
    assert utils.is_valid_passphrase('a nice lengthy förmé')


def test_long_name_passes():
    assert utils.is_valid_name('Russel Winder')


def test_name_too_short_fails():
    assert not utils.is_valid_name('r')


@pytest.mark.parametrize('number', (
    '+44 20 7585 2200',
    '+442075852200',
    '020 7585 2200',
    '02075852200',
))
def test_valid_phone_numbers_pass(number):
    assert utils.is_valid_phone(number)


@pytest.mark.parametrize('number', (
    '+44-20-7585-2200',
    '020-7585-2200',
    'xxxxxxxxxx',
))
def test_non_itu_conforming_phone_numbers_fail(number):
    assert not utils.is_valid_phone(number)


@pytest.mark.parametrize('country', (
    'United Kingdom',
    'Denmark',
))
def test_known_country_is_valid_country(country):
    assert utils.is_valid_country(country)


def test_unknown_country_is_not_valid_country():
    assert not utils.is_valid_country('Middle Earth')


@pytest.mark.parametrize('state', (
    'Surrey',
    'Middlesex',
))
def test_is_state_a_valid_state(state):
    assert utils.is_valid_state(state)


@pytest.mark.parametrize('postal_code', (
    'SW11 1EN',
    '12345',
))
def test_is_valid_postal_code(postal_code):
    assert utils.is_valid_postal_code(postal_code)


@pytest.mark.parametrize('street_address', (
    '41 Buckmaster Road',
    '1 Pall Mall',
))
def test_is_valid_street_address(street_address):
    assert utils.is_valid_street_address(street_address)


@pytest.mark.parametrize(('a', 'b', 'r'), (
    ({'a': 1}, {'b': 2}, {'a': 1, 'b': 2}),
))
def test_md_works(a, b, r):
    assert utils.md(a, b) == r
