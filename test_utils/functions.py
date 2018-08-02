"""
Various bits of code used in various testing places.

The symbol accuconf must be defined prior to loading of this module.
"""

from accuconf_cfp import db
from accuconf_cfp.utils import hash_passphrase

from models.user import User
from models.proposal import Proposal, Presenter, ProposalPresenter


def get_and_check_content(client, url, code=200, includes=(), excludes=()):
    """
    Send a get to the client with the url, check that all the values are in the returned HTML.
    """
    rv = client.get(url)
    assert rv is not None
    assert rv.status_code == code, '######## Status code was {}, expected {}'.format(rv.status_code, code)
    rvd = rv.get_data().decode('utf-8')
    for item in includes:
        assert item in rvd, '######## `{}` not in\n{}'.format(item, rvd)
    for item in excludes:
        assert item not in rvd, '######## `{}` in\n{}'.format(item, rvd)
    return rvd


def post_and_check_content(client, url, data, content_type=None, code=200, includes=(), excludes=(), follow_redirects=False):
    """
    Send a post to the client with the url and data, of the content_type, and the check that all the values
    are in the returned HTML.
    """
    rv = client.post(url, data=data, content_type=content_type, follow_redirects=follow_redirects)
    assert rv is not None
    assert rv.status_code == code, '######## Status code was {}, expected {}'.format(rv.status_code, code)
    rvd = rv.get_data().decode('utf-8')
    for item in includes:
        assert item in rvd, '######## `{}` not in\n{}'.format(item, rvd)
    for item in excludes:
        assert item not in rvd, '######## `{}` in\n{}'.format(item, rvd)
    return rvd


def add_new_user(user_details):
    """Given a dictionary of user details create a user in the data base."""
    user = User(**user_details)
    user.passphrase = hash_passphrase(user.passphrase)
    db.session.add(user)
    db.session.commit()


def add_a_proposal_as_user(user_email, proposal_data):
    """Given a user email and a dictionary of details about a proposal add the proposal to the database."""
    user = User.query.filter_by(email=user_email).first()
    proposal = Proposal(
        user,
        proposal_data['title'],
        proposal_data['summary'],
        proposal_data['session_type'],
    )
    db.session.add(proposal)
    for presenter_data in proposal_data['presenters']:
        presenter = Presenter(
            presenter_data['email'],
            presenter_data['name'],
            presenter_data['bio'],
            presenter_data['country'],
        )
        db.session.add(presenter)
        ProposalPresenter(proposal, presenter, presenter_data['is_lead'])
    db.session.commit()
