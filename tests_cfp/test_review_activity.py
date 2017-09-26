import json

# Apparently unused but loading has crucial side effects
import configure

from accuconf_cfp import app, db
from accuconf_cfp.utils import hash_passphrase
from accuconf_cfp.views.review import already_reviewed

from models.proposal import Proposal
from models.role_types import Role
from models.score import Score
from models.user import User

# PyCharm fails to spot the use of this symbol as a fixture.
from fixtures import registrant

from test_utils.constants import (
    login_menu_item, logout_menu_item, my_proposals_menu_item,
    register_menu_item, registration_update_menu_item, submit_menu_item
)
# PyCharm fails to spot the use of symbols as fixtures.
from test_utils.fixtures import client, proposal_single_presenter, proposal_multiple_presenters_single_lead
from test_utils.functions import add_a_proposal_as_user, add_new_user, get_and_check_content, post_and_check_content

new_user = {
    'email': 'p@a.b.c',
    'passphrase': 'A passphrase',
    'name': 'A B C Person',
    'country': 'United Kingdom',
}


def test_already_reviewed(registrant, proposal_single_presenter, proposal_multiple_presenters_single_lead):
    reviewer = User(**new_user)
    proposer = User(**registrant)
    proposals = (
        Proposal(
            proposer,
            proposal_single_presenter['title'],
            proposal_single_presenter['session_type'],
            proposal_single_presenter['summary'],
        ),
        Proposal(
            proposer,
            proposal_multiple_presenters_single_lead['title'],
            proposal_multiple_presenters_single_lead['session_type'],
            proposal_multiple_presenters_single_lead['summary'],
        )
    )
    assert not already_reviewed(proposals[0], reviewer)
    assert not already_reviewed(proposals[1], reviewer)
    score = Score(proposals[1], reviewer, 7)
    assert not already_reviewed(proposals[0], reviewer)
    assert already_reviewed(proposals[1], reviewer)


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
    add_new_user(new_user)
    add_a_proposal_as_user(new_user['email'], proposal_single_presenter())
    add_a_proposal_as_user(new_user['email'], proposal_multiple_presenters_single_lead())
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
    add_new_user(new_user)
    add_a_proposal_as_user(new_user['email'], proposal_single_presenter())
    add_a_proposal_as_user(new_user['email'], proposal_multiple_presenters_single_lead())
    test_reviewer_can_register_and_login(client, registrant, monkeypatch)
    get_and_check_content(client, '/review_proposal/1',
                          includes=(' – Proposal to Review',),
                          excludes=(),
                          )


def test_logged_in_reviewer_can_submit_score_for_not_own_entries(client, registrant, monkeypatch):
    test_logged_in_reviewer_can_get_review_proposal_for_not_own_entries(client, registrant, monkeypatch)
    post_and_check_content(client, '/review_proposal/1', json.dumps({'score': 7, 'comment': ''}), 'application/json',
                           includes=('Review stored.',),
                           excludes=(),
                           )


def test_logged_in_reviewer_can_update_a_review(client, registrant, monkeypatch):
    test_logged_in_reviewer_can_submit_score_for_not_own_entries(client, registrant, monkeypatch)
    post_and_check_content(client, '/review_proposal/1', json.dumps({'score': 6, 'comment': 'Not really very good.'}), 'application/json',
                           includes=('Review stored.',),
                           excludes=(),
                           )
    get_and_check_content(client, '/review_proposal/1',
                          includes=(' – Proposal to Review',),
                          excludes=(),
                          )
