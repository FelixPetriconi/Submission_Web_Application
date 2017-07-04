import pytest

from common import client, post_and_check_content


@pytest.fixture
def registrant():
    return {
        'email': 'a@b.c',
        'password': 'Password1',
        'cpassword': 'Password1',
        'name': 'User Name',
        'phone': '+011234567890',
        'pincode': '123456',
        'country': 'India',
        'state': 'TamilNadu',
        'towncity': 'Chennai',
        'streetaddress': 'Chepauk',
        'captcha': '1',
        'question': '12'
    }


def test_user_auth_basic(client, registrant):
    post_and_check_content(client, '/register', registrant)
    post_and_check_content(client, '/login',
                           {'email': 'a@b.c', 'password': 'Password1'},
                           values=('ACCU Conference',),
                           follow_redirects=True)


def test_user_auth_fail(client, registrant):
    post_and_check_content(client, '/register', registrant)
    post_and_check_content(client, '/login',
                           {'email': 'a@b.c', 'password': 'Password2'},
                           values=('Login',),
                           follow_redirects=True)
