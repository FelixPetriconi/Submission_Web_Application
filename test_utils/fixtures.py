"""
Various fixtures used in various testing places.
"""

import pytest

from accuconf import app, db

from models.proposal_types import SessionType, SessionAudience


@pytest.fixture
def database():
    """Deliver up the database associated with the application.

    Whatever the location of the database for the current configuration,
    override it for the tests.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield db
        db.session.rollback()
        db.drop_all()


@pytest.fixture()
def client():
    """A Werkzeug client in testing mode with a newly created database.

    Whatever the location of the database for the current configuration,
    override it for the tests.
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['DEBUG'] = False
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = "TheObviouslyOpenSecret"
    app.config['MAINTENANCE'] = False
    app.config['CALL_OPEN'] = False
    app.config['REVIEWING_ALLOWED'] = False
    app.config['ADMINISTERING'] = False
    app.config['API_ACCESS'] = False
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()
        db.session.rollback()
        db.drop_all()


@pytest.fixture
def registrant():
    return {
        'email': 'a@b.c',
        'passphrase': 'Passphrase for this user.',
        'cpassphrase': 'Passphrase for this user.',
        'name': 'User Name',
        'phone': '+011234567890',
        'country': 'India',
    }


@pytest.fixture
def proposal_single_presenter():
    return {
        'title': 'A single presenter proposal',
        'session_type': SessionType.quickie.value,
        'summary': '''This is a test proposal that will have
dummy data. Also this is not a very
lengthy proposal''',
        'audience': SessionAudience.expert.value,
        'notes': 'Please accept this proposal.',
        'constraints': 'None',
        'presenters': [
            {
                'email': 'a@b.c',
                'is_lead': True,
                'name': 'User Name',
                'bio': 'A nice member of the human race who has a good history of presentation.',
                'country': 'India',
            },
        ]
    }


@pytest.fixture
def proposal_multiple_presenters_single_lead():
    return {
        'title': 'A multi presenter proposal',
        'session_type': 'workshop',
        'summary': '''This is a proposal for a workshop that has
dummy data. Also this is not a very
lengthy proposal''',
        'presenters': [
            {
                'email': 'p1@b.c',
                'is_lead': True,
                'name': 'Presenter First',
                'bio': 'A person with a good history of presentations working with someone new to presenting.',
                'country': 'India',
            },
            {
                'email': 'p2@b.c',
                'is_lead': False,
                'name': 'Presenter Second',
                'bio': 'A person who is new to presentations but is doing it with a veteran ',
                'country': 'India',
            },
        ]
    }


@pytest.fixture
def proposal_multiple_presenters_and_leads():
    proposal_data = proposal_multiple_presenters_single_lead()
    assert not proposal_data['presenters'][1]['is_lead']
    proposal_data['presenters'][1]['is_lead'] = True
    return proposal_data


@pytest.fixture
def proposal_single_presenter_not_lead():
    proposal_data = proposal_single_presenter()
    assert proposal_data['presenters'][0]['is_lead']
    proposal_data['presenters'][0]['is_lead'] = False
    return proposal_data


@pytest.fixture
def proposal_single_presenter_lead_field_set_to_none():
    proposal_data = proposal_single_presenter()
    assert proposal_data['presenters'][0]['is_lead']
    proposal_data['presenters'][0]['is_lead'] = None
    return proposal_data


@pytest.fixture
def proposal_single_presenter_no_lead_field():
    proposal_data = proposal_single_presenter()
    assert proposal_data['presenters'][0]['is_lead']
    del proposal_data['presenters'][0]['is_lead']
    return proposal_data


@pytest.fixture
def proposal_single_presenter_summary_field_is_none():
    proposal_data = proposal_single_presenter()
    proposal_data['summary'] = None
    return proposal_data


@pytest.fixture
def proposal_single_presenter_no_summary_field():
    proposal_data = proposal_single_presenter()
    del proposal_data['summary']
    return proposal_data


@pytest.fixture
def proposal_single_presenter_title_field_too_short():
    proposal_data = proposal_single_presenter()
    proposal_data['title'] = 'fubar'
    return proposal_data


@pytest.fixture
def proposal_single_presenter_summary_field_too_short():
    proposal_data = proposal_single_presenter()
    proposal_data['summary'] = 'fubar'
    return proposal_data


@pytest.fixture
def proposal_single_presenter_presenters_field_empty_list():
    proposal_data = proposal_single_presenter()
    proposal_data['presenters'] = []
    return proposal_data


@pytest.fixture
def proposal_single_presenter_presenters_field_not_a_list():
    proposal_data = proposal_single_presenter()
    proposal_data['presenters'] = 'fubar'
    return proposal_data
