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

from test_utils.constants import login_menu_item, register_menu_item, registration_update_menu_item
# PyCharm fails to spot this is used as a fixture.
from test_utils.fixtures import client
from test_utils.functions import get_and_check_content, post_and_check_content

from accuconf_cfp.utils import hash_passphrase
from accuconf_cfp.views.submit import validate_presenters, validate_proposal_data


@pytest.fixture
def registration_data():
    return {
        'email': 'a@b.c',
        'passphrase': 'Passphrase for this user.',
        'name': 'User Name',
        'phone': '+011234567890',
        'country': 'India',
        'state': 'TamilNadu',
        'postal_code': '123456',
        'town_city': 'Chennai',
        'street_address': 'Chepauk',
    }


@pytest.fixture
def proposal_single_presenter():
    return {
        'proposer': 'a@b.c',
        'title': 'ACCU Proposal',
        'session_type': 'quickie',
        'summary': '''This is a test proposal that will have
dummy data. Also this is not a very
lengthy proposal''',
        'presenters': [
            {
                'email': 'a@b.c',
                'is_lead': True,
                'name': 'User Name',
                'bio': 'A nice member of the human race.',
                'country': 'India',
                'state': 'TamilNadu'
            },
        ]
    }


@pytest.fixture
def proposal_multiple_presenters_single_lead():
    return {
        'proposer': 'a@b.c',
        'title': 'ACCU Proposal',
        'session_type': 'miniworkshop',
        'summary': ''' This is a test proposal that will have
dummy data. Also this is not a very
lengthy proposal''',
        'presenters': [
            {
                'email': 'a@b.c',
                'is_lead': True,
                'name': 'User Name',
                'bio': 'A person.',
                'country': 'India',
                'state': 'TamilNadu'
            },
            {
                'email': 'p2@b.c',
                'is_lead': False,
                'name': 'Presenter Second',
                'bio': 'Another person',
                'country': 'India',
                'state': 'TamilNadu'
            },
        ]
    }


@pytest.fixture
def proposal_multiple_presenters_and_leads():
    proposal_data = proposal_multiple_presenters_single_lead()
    assert not proposal_data['presenters'][1]['is_lead']
    proposal_data['presenters'][1]['is_lead'] = True
    return proposal_data


def test_submit_not_available_when_not_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/submit',
                          code=302,
                          includes=('Redirect', '<a href="/">'),
                          excludes=(login_menu_item, register_menu_item),
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


def test_ensure_registration_and_login(client, registration_data, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    user = User.query.filter_by(email=registration_data['email']).all()
    assert len(user) == 0
    post_and_check_content(client, '/register', json.dumps(registration_data), 'application/json',
                           includes=('register_success',),
                           excludes=(),
                           )
    user = User.query.filter_by(email=registration_data['email']).all()
    assert len(user) == 1
    assert user[0].passphrase == hash_passphrase(registration_data['passphrase'])
    post_and_check_content(client, '/login', json.dumps({'email': registration_data['email'], 'passphrase': registration_data['passphrase']}), 'application/json',
                           includes=('login_success',),
                           excludes=(),
                           )


def test_not_logged_in_user_cannot_get_submission_page(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/submit',
                          includes=('Submit', 'You must be registered and logged in to submit a proposal.', login_menu_item, register_menu_item),
                          )


def test_logged_in_user_can_get_submission_page(client, registration_data, monkeypatch):
    test_ensure_registration_and_login(client, registration_data, monkeypatch)
    get_and_check_content(client, '/submit',
                          includes=('Submit',),
                          excludes=(login_menu_item, register_menu_item),
                          )


def test_logged_in_user_can_submit_a_single_presenter_proposal(client, registration_data, proposal_single_presenter, monkeypatch):
    test_ensure_registration_and_login(client, registration_data, monkeypatch)
    post_and_check_content(client, '/submit', json.dumps(proposal_single_presenter), 'application/json',
                           includes=('submit_success',),
                           excludes=(login_menu_item, register_menu_item),
                           )
    user = User.query.filter_by(email='a@b.c').all()
    assert len(user) == 1
    user = user[0]
    assert user is not None
    assert len(user.proposals) == 1
    proposal = user.proposals[0]
    assert proposal is not None
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


def test_get_submit_success_after_successful_submission(client, registration_data, proposal_single_presenter, monkeypatch):
    test_logged_in_user_can_submit_a_single_presenter_proposal(client, registration_data, proposal_single_presenter, monkeypatch)
    get_and_check_content(client, '/submit_success',
                          includes=('Submission Successful', 'Thank you, you have successfully submitted'),
                          excludes=(login_menu_item, register_menu_item),
                          )


def test_logged_in_user_can_submit_multipresenter_single_lead_proposal(client, registration_data, proposal_multiple_presenters_single_lead, monkeypatch):
    test_ensure_registration_and_login(client, registration_data, monkeypatch)
    post_and_check_content(client, '/submit', json.dumps(proposal_multiple_presenters_single_lead), 'application/json',
                           includes=('submit_success',),
                           excludes=(login_menu_item, register_menu_item),
                           )
    user = User.query.filter_by(email='a@b.c').all()
    assert len(user) == 1
    user = user[0]
    assert user is not None
    assert len(user.proposals) == 1
    proposal = user.proposals[0]
    assert proposal is not None
    assert proposal.session_type == SessionType.miniworkshop
    assert len(proposal.presenters) == 2
    assert len(proposal.proposal_presenters) == 2
    if proposal.proposal_presenters[0].is_lead:
        assert proposal.presenters[0].email == user.email
        assert proposal.presenters[1].email == 'p2@b.c'
    else:
        assert proposal.presenters[0].email == 'p2@b.c'
        assert proposal.presenters[1].email == user.email


def test_logged_in_user_cannot_submit_multipresenter_multilead_proposal(client, registration_data, proposal_multiple_presenters_and_leads, monkeypatch):
    test_ensure_registration_and_login(client, registration_data, monkeypatch)
    post_and_check_content(client, '/submit', json.dumps(proposal_multiple_presenters_and_leads), 'application/json',
                           code=400,
                           includes=("['a@b.c', 'p2@b.c'] marked as lead presenters",),
                           excludes=(login_menu_item, register_menu_item),
                           )
    user = User.query.filter_by(email='a@b.c').all()
    assert len(user) == 1
    user = user[0]
    assert user is not None
    assert len(user.proposals) == 0


def test_logged_in_get_proposals_page(client, registration_data, proposal_single_presenter, monkeypatch):
    test_logged_in_user_can_submit_a_single_presenter_proposal(client, registration_data, proposal_single_presenter, monkeypatch)
    get_and_check_content(client, '/my_proposals',
                          includes=(
                              'My Proposals',
                              'The following are your current proposals. Click on the one you wish to update.',
                              '<li><a href="/proposal_update/1"> ACCU Proposal </a></li>',
                              registration_update_menu_item,
                          ),
                          excludes=(login_menu_item, register_menu_item)
                          )


def test_not_logged_in_my_proposals_get_request_fails(client, registration_data, proposal_single_presenter, monkeypatch):
    test_logged_in_user_can_submit_a_single_presenter_proposal(client, registration_data, proposal_single_presenter, monkeypatch)
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


def test_logged_in_submit_proposal_then_update_it(client, registration_data, proposal_single_presenter, monkeypatch):
    test_logged_in_user_can_submit_a_single_presenter_proposal(client, registration_data, proposal_single_presenter, monkeypatch)
    get_and_check_content(client, '/proposal_update/1',
                          includes=(),
                          excludes=(),
                          )


def test_not_logged_in_submit_proposal_then_attempt_to_update_it_fails(client, registration_data, proposal_single_presenter, monkeypatch):
    test_logged_in_user_can_submit_a_single_presenter_proposal(client, registration_data, proposal_single_presenter, monkeypatch)
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


def test_attempt_get_sub_success_out_of_open_causes_redirect(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/submit_success',
                          code=302,
                          includes=('Redirecting', '<a href="/">'),
                          )


def proposal_single_presenter_not_lead():
    proposal_data = proposal_single_presenter()
    assert proposal_data['presenters'][0]['is_lead']
    proposal_data['presenters'][0]['is_lead'] = False
    return proposal_data


def proposal_single_presenter_lead_field_set_to_none():
    proposal_data = proposal_single_presenter()
    assert proposal_data['presenters'][0]['is_lead']
    proposal_data['presenters'][0]['is_lead'] = None
    return proposal_data


def proposal_single_presenter_no_lead_field():
    proposal_data = proposal_single_presenter()
    assert proposal_data['presenters'][0]['is_lead']
    del proposal_data['presenters'][0]['is_lead']
    return proposal_data


def proposal_single_presenter_summary_field_is_none():
    proposal_data = proposal_single_presenter()
    proposal_data['summary'] = None
    return proposal_data


def proposal_single_presenter_no_summary_field():
    proposal_data = proposal_single_presenter()
    del proposal_data['summary']
    return proposal_data


def proposal_single_presenter_title_field_too_short():
    proposal_data = proposal_single_presenter()
    proposal_data['title'] = 'fubar'
    return proposal_data


def proposal_single_presenter_summary_field_too_short():
    proposal_data = proposal_single_presenter()
    proposal_data['summary'] = 'fubar'
    return proposal_data


def proposal_single_presenter_presenters_field_empty_list():
    proposal_data = proposal_single_presenter()
    proposal_data['presenters'] = []
    return proposal_data


def proposal_single_presenter_presenters_field_not_a_list():
    proposal_data = proposal_single_presenter()
    proposal_data['presenters'] = 'fubar'
    return proposal_data


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
