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
        'country': 'India',
        'state': 'TamilNadu',
        'postalcode': '123456',
        'towncity': 'Chennai',
        'streetaddress': 'Chepauk',
        'captcha': '1',
        'question': '12'
    }


def test_successful_login(client, registrant):
    post_and_check_content(client, '/register', registrant)
    post_and_check_content(client, '/login',
                           {'email': registrant.email, 'passphrase':  registrant.passphrase},
                           includes=('ACCU Conference',),
                           follow_redirects=True)


def test_wrong_passphrase_causes_login_failure(client, registrant):
    post_and_check_content(client, '/register', registrant)
    post_and_check_content(client, '/login',
                           {'email': registrant.email, 'passphrase': 'Passphrase2'},
                           includes=('Login',),
                           follow_redirects=True)


def test_update_user_name(client, registrant):
    test_successful_login(client, registrant)
    registrant['name'] = 'Some Dude'
    post_and_check_content(client, '/register', registrant, includes=('Your account details were successful updated.',))
