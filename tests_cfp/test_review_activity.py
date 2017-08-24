import json

# Apparently unused but loading has crucial side effects
import configure

from accuconf_cfp import app, db
from accuconf_cfp.utils import hash_passphrase

from models.user import User
from models.role_types import Role

# PyCharm fails to spot the use of this symbol as a fixture.
from fixtures import registrant

from test_utils.constants import (
    login_menu_item, logout_menu_item, my_proposals_menu_item,
    register_menu_item, registration_update_menu_item, submit_menu_item
)
# PyCharm fails to spot the use of symbols as fixtures.
from test_utils.fixtures import client, proposal_single_presenter, proposal_multiple_presenters_single_lead
from test_utils.functions import add_a_proposal_as_user, add_new_user, get_and_check_content, post_and_check_content


def test_attempt_to_get_review_list_page_outside_open_period_causes_redirect(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/review_list',
                          code=302,
                          includes=('Redirect', '<a href="/">'),
                          )


def test_user_not_a_reviewer_can_register_and_login(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    post_and_check_content(client, '/register', json.dumps(registrant), 'application/json',
                           includes=('register_success',),
                           excludes=(),
                           )
    get_and_check_content(client, '/register_success',
                          includes=(' – Registration Successful', 'You have successfully registered', login_menu_item, register_menu_item),
                          excludes=(logout_menu_item, my_proposals_menu_item, registration_update_menu_item, submit_menu_item),
                          )
    post_and_check_content(client, '/login',
                           json.dumps({'email': registrant['email'], 'passphrase': registrant['passphrase']}), 'application/json',
                           includes=('login_success',),
                           excludes=(),
                           )
    get_and_check_content(client, '/login_success',
                          includes=(' – Login Successful', 'Login successful', logout_menu_item, registration_update_menu_item),
                          excludes=(login_menu_item, my_proposals_menu_item, register_menu_item, submit_menu_item),
                          )


def test_user_not_a_reviewer_can_register_and_login_but_not_see_review_page(client, registrant, monkeypatch):
    test_user_not_a_reviewer_can_register_and_login(client, registrant, monkeypatch)
    get_and_check_content(client, '/review_list',
                          includes=(' – Review List Failed', 'Logged in user is not a registered reviewer.', logout_menu_item, registration_update_menu_item),
                          excludes=(login_menu_item, my_proposals_menu_item, register_menu_item, submit_menu_item),
                          )


def test_user_not_a_reviewer_can_register_and_login_but_not_see_review_proposal_page(client, registrant, monkeypatch):
    test_user_not_a_reviewer_can_register_and_login(client, registrant, monkeypatch)
    get_and_check_content(client, '/review_proposal/1',
                          includes=(' – Review Proposal Failed', 'Logged in user is not a registered reviewer.', logout_menu_item, registration_update_menu_item),
                          excludes=(login_menu_item, my_proposals_menu_item, register_menu_item, submit_menu_item),
                          )


def test_reviewer_can_register_and_login(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 0
    post_and_check_content(client, '/register', json.dumps(registrant), 'application/json',
                           includes=('register_success',),
                           excludes=(),
                           )
    get_and_check_content(client, '/register_success',
                          includes=(' – Registration Successful', 'You have successfully registered', login_menu_item, register_menu_item),
                          excludes=(logout_menu_item, my_proposals_menu_item, registration_update_menu_item, submit_menu_item),
                          )
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 1
    user = user[0]
    assert user.email == registrant['email']
    assert user.passphrase == hash_passphrase(registrant['passphrase'])
    assert user.role == Role.user
    user.role = Role.reviewer
    db.session.commit()
    post_and_check_content(client, '/login',
                           json.dumps({'email': registrant['email'], 'passphrase': registrant['passphrase']}), 'application/json',
                           includes=('login_success',),
                           excludes=(),
                           )
    get_and_check_content(client, '/login_success',
                          includes=(' – Login Successful', 'Login successful', logout_menu_item, registration_update_menu_item),
                          excludes=(login_menu_item, my_proposals_menu_item, register_menu_item, submit_menu_item),
                          )


def test_logged_in_reviewer_can_get_review_list(client, registrant, monkeypatch):
    test_reviewer_can_register_and_login(client, registrant, monkeypatch)
    get_and_check_content(client, '/review_list',
                          includes=(' – List of Proposals',),
                          excludes=(),
                          )


def test_logged_in_reviewer_can_get_review_list_and_see_all_not_own_entries(client, registrant, monkeypatch):
    user_email = 'p@a.b.c'
    add_new_user({
        'email': user_email,
        'passphrase': 'A passphrase',
        'name': 'A B C Person',
        'street_address': '1 Some Road',
        'town_city': 'Somewhere',
        'postal_code': '12345',
        'country': 'United Kingdom',
    })
    add_a_proposal_as_user(user_email, proposal_single_presenter())
    add_a_proposal_as_user(user_email, proposal_multiple_presenters_single_lead())
    test_reviewer_can_register_and_login(client, registrant, monkeypatch)
    get_and_check_content(client, '/review_list',
                          includes=(
                              ' – List of Proposals',
                              '<td><a href="/review_proposal/1">A single presenter proposal</a></td>',
                              '<td><a href="/review_proposal/2">A multi presenter proposal</a></td>'
                          ),
                          excludes=(),
                          )


def test_logged_in_reviewer_can_get_review_list_and_see_no_own_entries(client, registrant, monkeypatch):
    test_reviewer_can_register_and_login(client, registrant, monkeypatch)
    add_a_proposal_as_user(registrant['email'], proposal_single_presenter())
    add_a_proposal_as_user(registrant['email'], proposal_multiple_presenters_single_lead())
    get_and_check_content(client, '/review_list',
                          includes=(' – List of Proposals',),
                          excludes=(
                              '<td><a href="/review_proposal/1">A single presenter proposal</a></td>',
                              '<td><a href="/review_proposal/2">A multi presenter proposal</a></td>'
                          ),
                          )


def test_logged_in_reviewer_can_get_review_proposal_for_not_own_entries(client, registrant, monkeypatch):
    user_email = 'p@a.b.c'
    add_new_user({
        'email': user_email,
        'passphrase': 'A passphrase',
        'name': 'A B C Person',
        'street_address': '1 Some Road',
        'town_city': 'Somewhere',
        'postal_code': '12345',
        'country': 'United Kingdom',
    })
    add_a_proposal_as_user(user_email, proposal_single_presenter())
    add_a_proposal_as_user(user_email, proposal_multiple_presenters_single_lead())
    test_reviewer_can_register_and_login(client, registrant, monkeypatch)
    get_and_check_content(client, '/review_proposal/1',
                          includes=(
                              ' – Proposals to Review',
                          ),
                          excludes=(),
                          )
