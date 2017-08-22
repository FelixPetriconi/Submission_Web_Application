import json

# Apparently unused but loading has crucial side effects
import configure

from accuconf import app

from models.user import User

# PyCharm fails to spot the use of this symbol as a fixture.
from fixtures import registrant

from test_utils.constants import login_menu_item, register_menu_item
# PyCharm fails to spot the use of this symbol as a fixture.
from test_utils.fixtures import client
from test_utils.functions import get_and_check_content, post_and_check_content

from accuconf_cfp.utils import hash_passphrase


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
    get_and_check_content(client, '/register_success',
                          includes=(' – Registration Successful', 'You have successfully registered'),
                          excludes=(),
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


def test_successful_login_checking_after_redirect(client, registrant, monkeypatch):
    test_successful_login(client, registrant, monkeypatch)
    get_and_check_content(client, '/login_success',
                          includes=(' – Login Successful', 'Login successful'),
                          excludes=(),
                          )


def test_logged_in_user_cannot_register(client, registrant, monkeypatch):
    test_successful_login(client, registrant, monkeypatch)
    post_and_check_content(client, '/register',
                           json.dumps({'email': registrant['email'], 'passphrase': registrant['passphrase']}), 'application/json',
                           code=302,
                           includes=('Redirect', '<a href="/">',),
                           excludes=(),
                           )


def test_logged_in_user_cannot_login_again(client, registrant, monkeypatch):
    test_successful_login(client, registrant, monkeypatch)
    post_and_check_content(client, '/login',
                           json.dumps(registrant), 'application/json',
                           code=302,
                           includes=('Redirect', '<a href="/">',),
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


def test_logout_not_in_open_state_cases_redirect(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/logout',
                          code=302,
                          includes=('Redirecting', '<a href="/">'),
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


def test_attempt_get_login_success_out_of_open_causes_redirect(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/login_success',
                          code=302,
                          includes=('Redirecting', '<a href="/">'),
                          )


def test_attempt_to_get_login_success_not_after_login_causes_redirect(client, registrant, monkeypatch):
    test_user_can_register(client, registrant, monkeypatch)
    get_and_check_content(client, '/login_success',
                          code=302,
                          includes=('Redirecting', '<a href="/">'),
                          )


def test_logged_in_user_can_get_registration_update_page(client, registrant, monkeypatch):
    test_successful_login(client, registrant, monkeypatch)
    get_and_check_content(client, '/registration_update',
                          includes=(' – Registration Details Updating',),
                          excludes=(),
                          )


def test_registration_update(client, registrant, monkeypatch):
    test_successful_login(client, registrant, monkeypatch)
    monkeypatch.setitem(registrant, 'name', 'Jo Bloggs')
    post_and_check_content(client, '/registration_update', json.dumps(registrant), 'application/json',
                           includes=('registration_update_success',),
                           excludes=(),
                           )


def test_get_registration_update_success_after_correct_registration_update(client, registrant, monkeypatch):
    test_registration_update(client, registrant, monkeypatch)
    get_and_check_content(client, '/registration_update_success',
                          includes=(' – Registration Update Successful', 'Your registration details were successfully updated.'),
                          excludes=(),
                          )
