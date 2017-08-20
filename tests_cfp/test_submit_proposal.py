"""
Tests for submitting a proposal.
"""

import json

import pytest

# Apparently unused but loading has crucial side effects.
import configure

from accuconf import app

from models.user import User
from models.proposal_types import SessionType

# PyCharm fails to spot the use of this symbol as a fixture.
from fixtures import registrant

from test_utils.constants import login_menu_item, register_menu_item, registration_update_menu_item
# PyCharm fails to spot this is used as a fixture.
from test_utils.fixtures import (client,
                                 proposal_single_presenter, proposal_multiple_presenters_single_lead,
                                 proposal_single_presenter_not_lead, proposal_single_presenter_lead_field_set_to_none,
                                 proposal_single_presenter_no_lead_field, proposal_multiple_presenters_and_leads,
                                 proposal_single_presenter_summary_field_is_none, proposal_single_presenter_no_summary_field,
                                 proposal_single_presenter_title_field_too_short, proposal_single_presenter_summary_field_too_short,
                                 proposal_single_presenter_presenters_field_empty_list, proposal_single_presenter_presenters_field_not_a_list,
                                 )
from test_utils.functions import get_and_check_content, post_and_check_content

from accuconf_cfp.utils import hash_passphrase
from accuconf_cfp.views.submit import validate_presenters, validate_proposal_data


def test_submit_not_available_when_not_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/submit',
                          code=302,
                          includes=('Redirect', '<a href="/">'),
                          excludes=(login_menu_item, register_menu_item),
                          )


def test_submit_success_not_available_when_not_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/submit_success',
                          code=302,
                          includes=('Redirecting', '<a href="/">'),
                          )


def test_my_proposals_not_available_when_not_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/my_proposals',
                          code=302,
                          includes=('Redirect', '<a href="/">'),
                          excludes=(login_menu_item, register_menu_item),
                          )


def test_proposals_update_not_available_when_not_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/proposal_update/0',
                          code=302,
                          includes=('Redirect', '<a href="/">'),
                          excludes=(login_menu_item, register_menu_item),
                          )


def test_proposal_update_success_not_available_when_not_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/proposal_update_success',
                          code=302,
                          includes=('Redirecting', '<a href="/">'),
                          )


@pytest.mark.parametrize('presenters', (
    proposal_single_presenter()['presenters'],
    proposal_multiple_presenters_single_lead()['presenters'],
))
def test_validate_presenters_works_with_valid_data(presenters):
    status, message = validate_presenters(presenters)
    assert status
    assert message == 'validated'


@pytest.mark.parametrize('presenters', (
    proposal_single_presenter_not_lead()['presenters'],
    proposal_single_presenter_lead_field_set_to_none()['presenters'],
    proposal_single_presenter_no_lead_field()['presenters'],
    proposal_multiple_presenters_and_leads()['presenters'],
))
def test_validate_presenters_fails_with_invalid_data(presenters):
    status, message = validate_presenters(presenters)
    assert not status


@pytest.mark.parametrize('proposal', (
    proposal_single_presenter(),
    proposal_multiple_presenters_single_lead(),
))
def test_validate_proposal_data_succeeds_with_reasonable_data(proposal):
    status, message = validate_proposal_data(proposal)
    assert status
    assert message == 'validated'


@pytest.mark.parametrize('proposal', (
    proposal_single_presenter_not_lead(),
    proposal_single_presenter_lead_field_set_to_none(),
    proposal_single_presenter_no_lead_field(),
    proposal_single_presenter_summary_field_is_none(),
    proposal_single_presenter_no_summary_field(),
    proposal_single_presenter_title_field_too_short(),
    proposal_single_presenter_summary_field_too_short(),
    proposal_single_presenter_presenters_field_empty_list(),
    proposal_single_presenter_presenters_field_not_a_list(),
    proposal_multiple_presenters_and_leads(),
))
def test_validate_proposal_data_fails_with_invalid_data(proposal):
    status, message = validate_proposal_data(proposal)
    assert not status


def test_ensure_registration_and_login(client, registrant, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 0
    post_and_check_content(client, '/register', json.dumps(registrant), 'application/json',
                           includes=('register_success',),
                           excludes=(),
                           )
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 1
    assert user[0].passphrase == hash_passphrase(registrant['passphrase'])
    post_and_check_content(client, '/login', json.dumps({'email': registrant['email'], 'passphrase': registrant['passphrase']}), 'application/json',
                           includes=('login_success',),
                           excludes=(),
                           )


def test_not_logged_in_user_cannot_get_submission_page(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/submit',
                          includes=('Submit', 'You must be registered and logged in to submit a proposal.', login_menu_item, register_menu_item),
                          )


def test_logged_in_user_can_get_submission_page(client, registrant, monkeypatch):
    test_ensure_registration_and_login(client, registrant, monkeypatch)
    get_and_check_content(client, '/submit',
                          includes=('Submit',),
                          excludes=(login_menu_item, register_menu_item),
                          )


def test_logged_in_user_can_submit_a_single_presenter_proposal(client, registrant, proposal_single_presenter, monkeypatch):
    test_ensure_registration_and_login(client, registrant, monkeypatch)
    post_and_check_content(client, '/submit', json.dumps(proposal_single_presenter), 'application/json',
                           includes=('submit_success',),
                           excludes=(login_menu_item, register_menu_item),
                           )
    get_and_check_content(client, '/submit_success',
                          includes=('Submission Successful', 'Thank you, you have successfully submitted'),
                          excludes=(login_menu_item, register_menu_item),
                          )
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 1
    user = user[0]
    assert user is not None
    assert len(user.proposals) == 1
    proposal = user.proposals[0]
    assert proposal is not None
    assert proposal.title == proposal_single_presenter['title']
    assert proposal.session_type == SessionType.quickie
    assert len(proposal.presenters) == 1
    presenter = proposal.presenters[0]
    assert presenter.email == user.email
    assert len(proposal.proposal_presenters) == 1
    p = proposal.proposal_presenters[0]
    assert p.proposal == proposal
    assert p.presenter == presenter
    assert p.is_lead
    assert len(presenter.presenter_proposals) == 1
    pp = presenter.presenter_proposals[0]
    assert p == pp


def test_logged_in_user_can_submit_multipresenter_single_lead_proposal(client, registrant, proposal_multiple_presenters_single_lead, monkeypatch):
    test_ensure_registration_and_login(client, registrant, monkeypatch)
    post_and_check_content(client, '/submit', json.dumps(proposal_multiple_presenters_single_lead), 'application/json',
                           includes=('submit_success',),
                           excludes=(login_menu_item, register_menu_item),
                           )
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 1
    user = user[0]
    assert user is not None
    assert len(user.proposals) == 1
    proposal = user.proposals[0]
    assert proposal is not None
    assert proposal.session_type == SessionType.miniworkshop
    presenters = proposal.presenters
    proposal_presenters = proposal.proposal_presenters
    assert len(presenters) == 2
    assert len(proposal_presenters) == 2
    original_presenters = proposal_multiple_presenters_single_lead['presenters']
    if proposal_presenters[0].is_lead:
        assert presenters[0].email == original_presenters[0]['email']
        assert presenters[1].email == original_presenters[1]['email']
    else:
        assert presenters[0].email == original_presenters[1]['email']
        assert presenters[1].email == original_presenters[0]['email']


def test_logged_in_user_cannot_submit_multipresenter_multilead_proposal(client, registrant, proposal_multiple_presenters_and_leads, monkeypatch):
    test_ensure_registration_and_login(client, registrant, monkeypatch)
    presenters = proposal_multiple_presenters_and_leads['presenters']
    post_and_check_content(client, '/submit', json.dumps(proposal_multiple_presenters_and_leads), 'application/json',
                           code=400,
                           includes=("['{}', '{}'] marked as lead presenters".format(presenters[0]['email'], presenters[1]['email']),),
                           excludes=(login_menu_item, register_menu_item),
                           )
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 1
    user = user[0]
    assert user is not None
    assert len(user.proposals) == 0


def test_logged_in_get_my_proposals_page(client, registrant, proposal_single_presenter, monkeypatch):
    test_logged_in_user_can_submit_a_single_presenter_proposal(client, registrant, proposal_single_presenter, monkeypatch)
    get_and_check_content(client, '/my_proposals',
                          includes=(
                              'My Proposals',
                              'The following are your current proposals.',
                              '<li class="proposal-list"><a href="/proposal_update/1"> A single presenter proposal </a></li>',
                              registration_update_menu_item,
                          ),
                          excludes=(login_menu_item, register_menu_item)
                          )


def test_not_logged_in_my_proposals_get_request_fails(client, registrant, proposal_single_presenter, monkeypatch):
    test_logged_in_user_can_submit_a_single_presenter_proposal(client, registrant, proposal_single_presenter, monkeypatch)
    get_and_check_content(client, '/logout',
                          code=302,
                          includes=('Redirect', '<a href="/">'),
                          )
    monkeypatch.setitem(proposal_single_presenter, 'title', 'Something Interesting')
    get_and_check_content(client, '/my_proposals',
                          includes=(
                              'My Proposals Failure',
                              'You must be registered and logged in to discover your current proposals.',
                              login_menu_item,
                              register_menu_item,
                          ),
                          excludes=(),
                          )


def test_logged_in_submit_proposal_then_update_it(client, registrant, proposal_single_presenter, monkeypatch):
    test_logged_in_user_can_submit_a_single_presenter_proposal(client, registrant, proposal_single_presenter, monkeypatch)
    get_and_check_content(client, '/proposal_update/1',
                          includes=(proposal_single_presenter['title'], proposal_single_presenter['presenters'][0]['email']),
                          excludes=(),
                          )


def test_not_logged_in_submit_proposal_then_attempt_to_update_it_fails(client, registrant, proposal_single_presenter, monkeypatch):
    test_logged_in_user_can_submit_a_single_presenter_proposal(client, registrant, proposal_single_presenter, monkeypatch)
    get_and_check_content(client, '/logout',
                          code=302,
                          includes=('Redirect', '<a href="/">'),
                          )
    get_and_check_content(client, '/proposal_update/1',
                          includes=(
                              'Proposal Update Failure',
                              'You must be registered and logged in to update a proposal.',
                              login_menu_item,
                              register_menu_item,
                          ),
                          excludes=(),
                          )


def test_logged_in_user_can_update_a_previously_submitted_single_presenter_proposal(client, registrant, proposal_single_presenter, monkeypatch):
    test_logged_in_user_can_submit_a_single_presenter_proposal(client, registrant, proposal_single_presenter, monkeypatch)
    alternate_title = 'This is an alternate title'
    alternate_email = 'x@y.z'
    monkeypatch.setitem(proposal_single_presenter, 'title', alternate_title)
    monkeypatch.setitem(proposal_single_presenter['presenters'][0], 'email', alternate_email)
    post_and_check_content(client, '/proposal_update/1', json.dumps(proposal_single_presenter), 'application/json',
                           includes=('proposal_update_success',),
                           excludes=(login_menu_item, register_menu_item),
                           )
    get_and_check_content(client, '/proposal_update_success',
                          includes=('Update Successful', 'Thank you, you have successfully updated'),
                          excludes=(login_menu_item, register_menu_item),
                          )
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 1
    user = user[0]
    assert user is not None
    assert len(user.proposals) == 1
    proposal = user.proposals[0]
    assert proposal is not None
    assert proposal.title == alternate_title
    assert proposal.session_type == SessionType.quickie
    assert len(proposal.presenters) == 1
    presenter = proposal.presenters[0]
    assert presenter.email == alternate_email
    assert len(proposal.proposal_presenters) == 1
    p = proposal.proposal_presenters[0]
    assert p.proposal == proposal
    assert p.presenter == presenter
    assert p.is_lead
    assert len(presenter.presenter_proposals) == 1
    pp = presenter.presenter_proposals[0]
    assert p == pp


def test_logged_in_user_can_update_a_previously_submitted_multiple_presenter_proposal(client, registrant, proposal_multiple_presenters_single_lead, monkeypatch):
    test_logged_in_user_can_submit_multipresenter_single_lead_proposal(client, registrant, proposal_multiple_presenters_single_lead, monkeypatch)
    alternate_title = 'This is an alternate title'
    alternate_email = 'x@y.z'
    monkeypatch.setitem(proposal_multiple_presenters_single_lead, 'title', alternate_title)
    monkeypatch.setitem(proposal_multiple_presenters_single_lead['presenters'][1], 'email', alternate_email)
    post_and_check_content(client, '/proposal_update/1', json.dumps(proposal_multiple_presenters_single_lead), 'application/json',
                           includes=('proposal_update_success',),
                           excludes=(login_menu_item, register_menu_item),
                           )
    get_and_check_content(client, '/proposal_update_success',
                          includes=('Update Successful', 'Thank you, you have successfully updated'),
                          excludes=(login_menu_item, register_menu_item),
                          )
    user = User.query.filter_by(email=registrant['email']).all()
    assert len(user) == 1
    user = user[0]
    assert user is not None
    assert len(user.proposals) == 1
    proposal = user.proposals[0]
    assert proposal is not None
    assert proposal.title == alternate_title
    assert proposal.session_type == SessionType.miniworkshop
    presenters = proposal.presenters
    proposal_presenters = proposal.proposal_presenters
    assert len(presenters) == 2
    assert len(proposal_presenters) == 2
    presenter = proposal.presenters[1]
    assert presenter.email == alternate_email
    original_presenters = proposal_multiple_presenters_single_lead['presenters']
    if proposal_presenters[0].is_lead:
        assert presenters[0].email == original_presenters[0]['email']
        assert presenters[1].email == original_presenters[1]['email']
    else:
        assert presenters[0].email == original_presenters[1]['email']
        assert presenters[1].email == original_presenters[0]['email']
