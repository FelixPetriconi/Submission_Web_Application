import pytest

from common import client, get_and_check_content, post_and_check_content


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
                           {'email': registrant['email'], 'passphrase':  registrant['passphrase']},
                           code=302,
                           includes=('Redirecting', '<a href="/">',),
                           )


def test_wrong_passphrase_causes_login_failure(client, registrant):
    post_and_check_content(client, '/register', registrant)
    post_and_check_content(client, '/login',
                           {'email': registrant['email'], 'passphrase': 'Passphrase2'},
                           code=302,
                           includes=('Redirect', '<a href="/login">',),
                           )


def test_update_user_name(client, registrant):
    test_successful_login(client, registrant)
    registrant['name'] = 'Some Dude'
    post_and_check_content(client, '/register', registrant, includes=('Your account details were successful updated.',))


def test_logout_without_login_is_noop(client):
    get_and_check_content(client, '/logout', code=302, includes=('Redirect', '<a href="/">',))


def test_logged_in_user_can_logout_with_get(client, registrant):
    test_successful_login(client, registrant)
    get_and_check_content(client, '/logout', code=302, includes=('Redirect', '<a href="/">',))


def test_logged_in_user_cannot_logout_with_post(client, registrant):
    test_successful_login(client, registrant)
    post_and_check_content(client, '/logout', registrant, code=405, includes=('Method Not Allowed',))
