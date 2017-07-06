import pytest

from common import client, post_and_check_content


@pytest.fixture
def registrant():
    return {
        'email': 'a@b.c',
        'passphrase': 'Passphrase1',
        'cpassphrase': 'Passphrase1',
        'name': 'User Name',
        'phone': '+011234567890',
        'postcode': '123456',
        'country': 'India',
        'state': 'TamilNadu',
        'towncity' : 'Chennai',
        'streetaddress': 'Chepauk',
        'captcha': '1',
        'question': '12',
    }


def test_user_reg_basic(client, registrant):
    post_and_check_content(client, '/register', registrant, values=('You have successfully registered', 'Please login'))


def test_user_reg_dup(client, registrant):
    test_user_reg_basic(client, registrant)
    post_and_check_content(client, '/register', registrant, values=('Duplicate user email',))


def test_passphrase_short(client):
    post_and_check_content(client, '/register', {
        'email': 'test@std.dom',
        'passphrase': 'Pass1',
        'cpassphrase': 'Pass1',
        'name': 'User2 Name2',
        'phone': '+011234567890',
        'postcode': '123456',
        'country': 'India',
        'state': 'TamilNadu',
        'towncity' : 'Chennai',
        'streetaddress': 'Chepauk',
        'captcha': '1',
        'question': '12',
    }, values=('Passphrase did not meet checks',))


def test_passphrase_invalid(client):
    post_and_check_content(client, '/register', {
        'email': 'test@std.dom',
        'passphrase': 'passphrase',
        'cpassphrase': 'passphrase',
        'name': 'User2 Name2',
        'phone': '+011234567890',
        'postcode': '123456',
        'country': 'India',
        'state': 'TamilNadu',
        'towncity' : 'Chennai',
        'streetaddress': 'Chepauk',
        'bio': 'An individual of the world.',
        'captcha': '1',
        'question': '12'
    }, values=('Passphrase did not meet checks',))


def test_username_invalid(client):
    post_and_check_content(client, '/register', {
        'email': 'testing@test.dom',
        'passphrase': 'passphrase13',
        'cpassphrase': 'passphrase13',
        'name': 'User2 Name2',
        'phone': '+011234567890',
        'postcode': '123456',
        'country': 'India',
        'state': 'TamilNadu',
        'towncity' : 'Chennai',
        'streetaddress': 'Chepauk',
        'bio': 'An individual of the world.',
        'captcha': '1',
        'question': '12',
    }, values=('Invalid/Duplicate user email',))
