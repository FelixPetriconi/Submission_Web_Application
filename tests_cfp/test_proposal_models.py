"""
Test putting instances of various proposal related types into the database
and retrieving values and creating new instances of equal value..
"""

# Apparently unused but loading has crucial side effects
import configure

from models.user import User
from models.proposal import Proposal, Presenter, ProposalPresenter
from models.score import Score, Comment
from utils.proposals import SessionType, ProposalState, SessionCategory, SessionAudience

# PyCharm believes it isn't a used symbol, but it is.
from test_utils.fixtures import database

user_data = {
    'email': 'abc@b.c',
    'passphrase': 'passphrase',
    'name': 'User Name',
    'country': 'IND',
    'state': 'KARNATAKA',
    'postalcode': '560093',
    'towncity': 'Town',
    'address': 'Address',
    'phone': '+01234567890',
}

presenter_data = {
    'email': user_data['email'],
    'name': user_data['name'],
    'bio': 'A member of the human race.',
    'country': user_data['country'],
}

proposal_data = {
    'title': 'TDD with C++',
    'session_type': SessionType.quickie,
    'text': 'A session about creating C++ programs with proper process.',
    'notes': 'Some notes to the committee',
    'audience': SessionAudience.intermediate,
    'category': SessionCategory.agile,
}


def test_putting_proposal_in_database(database):
    user = User(*user_data)
    proposal = Proposal(user, *proposal_data)
    presenter = Presenter(*presenter_data)
    proposal_presenter = ProposalPresenter(proposal, presenter, True)
    # proposal.presenters.append(proposal_presenter)
    # presenter.proposals.append(proposal_presenter)
    database.session.add(user)
    database.session.add(proposal)
    database.session.add(presenter)
    database.session.add(proposal_presenter)
    database.session.commit()
    query_result = Proposal.query.filter_by(proposer_id=user.id).all()
    assert len(query_result) == 1
    proposal = query_result[0]
    assert proposal.proposer.email == user.email
    assert (proposal.title, proposal.session_type, proposal.text, proposal.notes, proposal.audience, proposal.category) == proposal_data
    assert proposal.status == ProposalState.submitted
    assert len(proposal.presenters) == 1
    proposal_presenter = proposal.presenters[0]
    is_lead = proposal_presenter.is_lead
    assert is_lead
    proposal_presenter = proposal_presenter.presenter
    assert (proposal_presenter.email, proposal_presenter.name) == (user.email, user.name)


def test_adding_review_and_comment_to_proposal_in_database(database):
    user = User(*user_data)
    proposal = Proposal(user, *proposal_data)
    presenter = Presenter(*presenter_data)
    proposal_presenter = ProposalPresenter(proposal, presenter, True)
    proposal.presenters.append(proposal_presenter)
    presenter.proposals.append(proposal_presenter)
    score = Score(proposal, user, 10)
    comment = Comment(proposal, user, 'Perfect')
    database.session.add(user)
    database.session.add(proposal)
    database.session.add(presenter)
    database.session.add(proposal_presenter)
    database.session.add(score)
    database.session.add(comment)
    database.session.commit()
    query_result = Proposal.query.filter_by(proposer_id=user.id).all()
    assert len(query_result) == 1
    proposal = query_result[0]
    assert proposal.scores is not None
    assert len(proposal.scores) == 1
    assert proposal.scores[0].score == 10
    assert proposal.comments is not None
    assert len(proposal.comments) == 1
    assert proposal.comments[0].comment == 'Perfect'
