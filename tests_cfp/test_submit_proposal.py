"""
Tests for submitting a proposal.
"""

import json

import pytest

# Apparently unused but loading has crucial side effects.
import configure

from accuconf import app

from models.user import User
from models.proposal import Proposal
from utils.proposals import SessionType

from test_utils.constants import login_menu_item, register_menu_item
# PyCharm fails to spot this is used as a fixture.
from test_utils.fixtures import client
from test_utils.functions import get_and_check_content, post_and_check_content


@pytest.fixture()
def registration_data():
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
        'question': '12',
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
    post_and_check_content(client, '/register', registration_data, includes=('You have successfully registered',))
    post_and_check_content(client, '/login', {'email': registration_data['email'], 'passphrase': registration_data['passphrase']}, code=302, includes=('Redirecting',))


def test_not_logged_in_user_cannot_get_submission_page(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    monkeypatch.setitem(app.config, 'MAINTENANCE', False)
    get_and_check_content(client, '/submit', includes=('Failure', 'Must be logged in to submit a proposal.', login_menu_item, register_menu_item))


def test_logged_in_user_can_get_submission_page(client, registration_data, monkeypatch):
    test_ensure_registration_and_login(client, registration_data, monkeypatch)
    get_and_check_content(client, '/submit', includes=('Submit',), excludes=(login_menu_item, register_menu_item))


def XXX__test_logged_in_user_can_submit_a_single_presenter_proposal(client, registration_data, proposal_single_presenter, monkeypatch):
    test_ensure_registration_and_login(client, registration_data, monkeypatch)
    rvd = post_and_check_content(client, '/submit', json.dumps(proposal_single_presenter), 'application/json', includes=('success',))
    response = json.loads(rvd)
    assert response['success']
    user = User.query.filter_by(email='a@b.c').all()
    assert len(user) == 1
    user = user[0]
    assert user is not None
    proposal = Proposal.query.filter_by(proposer_id=user.id).all()
    assert len(proposal) == 1
    proposal = proposal[0]
    assert proposal is not None
    assert user.proposals is not None
    assert len(user.proposals) == 1
    p = user.proposals[0]
    assert len(p.presenters) == 1
    proposal_presenter = p.presenters[0]
    presenter = proposal_presenter.presenter
    is_lead = proposal_presenter.is_lead
    assert is_lead
    assert presenter.email == user.email
    assert proposal.session_type == SessionType.quickie


def XXX_test_logged_in_user_can_submit_multipresenter_single_lead_proposal(client, registration_data, proposal_multiple_presenters_single_lead):
    test_ensure_registration_and_login(client, registration_data)
    rvd = post_and_check_content(client, '/upload_proposal', json.dumps(proposal_multiple_presenters_single_lead), 'application/json', includes=('success',))
    response = json.loads(rvd)
    assert response['success']
    user = User.query.filter_by(email='a@b.c').all()
    assert len(user) == 1
    user = user[0]
    assert user is not None
    proposal = Proposal.query.filter_by(proposer_id=user.id).all()
    assert len(proposal) == 1
    proposal = proposal[0]
    assert proposal is not None
    assert user.proposals is not None
    p = user.proposals[0]
    assert len(p.presenters) == 2
    if p.presenters[0].is_lead:
        assert p.presenters[0].presenter.email == user.email
        assert p.presenters[1].presenter.email == 'p2@b.c'
    else:
        assert p.presenters[0].presenter.email == 'p2@b.c'
        assert p.presenters[1].presenter.email == user.email
    assert proposal.session_type == SessionType.miniworkshop


def XXX_test_logged_in_user_cannot_submit_multipresenter_multilead_proposal(client, registration_data, proposal_multiple_presenters_and_leads):
    test_ensure_registration_and_login(client, registration_data)
    rvd = post_and_check_content(client, '/upload_proposal', json.dumps(proposal_multiple_presenters_and_leads), 'application/json', includes=('success',))
    response = json.loads(rvd)
    assert response["success"] is False
    assert "message" in response
    assert "both marked as lead presenters" in response["message"]
    user = User.query.filter_by(email='a@b.c').all()
    assert len(user) == 1
    user = user[0]
    assert user is not None
    assert len(user.proposals) == 0
    proposal = Proposal.query.filter_by(proposer_id=user.id).all()
    assert len(proposal) == 0
