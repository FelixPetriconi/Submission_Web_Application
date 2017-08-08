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


@pytest.fixture()
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


@pytest.fixture()
def proposal_single_presenter():
    return {
        'proposer': 'a@b.c',
        'title': 'ACCU Proposal',
        'session_type': 'quickie',
        'abstract': '''This is a test proposal that will have
dummy data. Also this is not a very
lengthy proposal''',
        'presenters': [
            {
                'email': 'a@b.c',
                'lead': True,
                'name': 'User Name',
                'bio': 'A nice member of the human race.',
                'country': 'India',
                'state': 'TamilNadu'
            },
        ]
    }


@pytest.fixture()
def proposal_multiple_presenters_single_lead():
    return {
        'proposer': 'a@b.c',
        'title': 'ACCU Proposal',
        'session_type': 'miniworkshop',
        'abstract': ''' This is a test proposal that will have
dummy data. Also this is not a very
lengthy proposal''',
        'presenters': [
            {
                'email': 'a@b.c',
                'lead': True,
                'name': 'User Name',
                'bio': 'A person.',
                'country': 'India',
                'state': 'TamilNadu'
            },
            {
                'email': 'p2@b.c',
                'lead': False,
                'name': 'Presenter Second',
                'bio': 'Another person',
                'country': 'India',
                'state': 'TamilNadu'
            },
        ]
    }


@pytest.fixture()
def proposal_multiple_presenters_and_leads():
    proposal_data = proposal_multiple_presenters_single_lead()
    assert proposal_data['presenters'][1]['lead'] == 0
    proposal_data['presenters'][1]['lead'] = 1
    return proposal_data


def test_ensure_registration_and_login(client, registration_data, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    user = User.query.filter_by(email=registration_data['email']).all()
    assert len(user) == 0
    post_and_check_content(client, '/register', json.dumps(registration_data), 'application/json',
                           includes=('register_success',),
                           )
    user = User.query.filter_by(email=registration_data['email']).all()
    assert len(user) == 1
    assert user[0].passphrase == hash_passphrase(registration_data['passphrase'])
    post_and_check_content(client, '/login', json.dumps({'email': registration_data['email'], 'passphrase': registration_data['passphrase']}), 'application/json',
                           includes=('Login successful',),
                           excludes=(login_menu_item, register_menu_item),
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
    rvd = post_and_check_content(client, '/submit', json.dumps(proposal_single_presenter), 'application/json',
                                 includes=('success',),
                                 excludes=(login_menu_item, register_menu_item),
                                 )
    response = json.loads(rvd)
    assert response['success']
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


def test_logged_in_user_can_submit_multipresenter_single_lead_proposal(client, registration_data, proposal_multiple_presenters_single_lead, monkeypatch):
    test_ensure_registration_and_login(client, registration_data, monkeypatch)
    rvd = post_and_check_content(client, '/submit', json.dumps(proposal_multiple_presenters_single_lead), 'application/json',
                                 includes=('success',),
                                 excludes=(login_menu_item, register_menu_item),
                                 )
    response = json.loads(rvd)
    assert response['success']
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
    rvd = post_and_check_content(client, '/submit', json.dumps(proposal_multiple_presenters_and_leads), 'application/json',
                                 includes=('success',),
                                 excludes=(login_menu_item, register_menu_item),
                                 )
    response = json.loads(rvd)
    assert response["success"] is False
    assert "message" in response
    assert "both marked as lead presenters" in response["message"]
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
