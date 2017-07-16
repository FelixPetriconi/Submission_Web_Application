"""
Test putting instances of various proposal related types into the database
and retrieving values and creating new instances of equal value..
"""

# Import the fixture, PyCharm believes it isn't a used symbol, but it is.
from common import database

from models.user import User
from models.proposal import Proposal, Presenter, ProposalPresenter, Score, Comment
from utils.proposals import SessionType, ProposalState, SessionCategory, SessionAudience

user_data = (
    'abc@b.c',
    'passphrase',
    'User Name',
    '+01234567890',
    'IND',
    'KARNATAKA',
    '560093',
    'Town',
    'Address',
)

proposal_data = (
    'TDD with C++',
    SessionType.quickie,
    'A session about creating C++ programs with proper process.',
    'Some notes to the committee',
    SessionAudience.intermediate,
    SessionCategory.agile,
)


def test_putting_proposal_in_database(database):
    user = User(*user_data)
    proposal = Proposal(user, *proposal_data)
    presenter_data = (user.email, user.name, 'A member of the human race.', user.country, user.state)
    presenter = Presenter(*presenter_data)
    database.session.add(user)
    database.session.add(proposal)
    database.session.add(presenter)
    database.session.commit()
    proposal_presenter = ProposalPresenter(proposal.id, presenter.id, proposal, presenter, True)
    proposal.presenters.append(proposal_presenter)
    presenter.proposals.append(proposal_presenter)
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
    presenter = Presenter(user.email, user.name, 'Someone that exists', user.country, user.state)
    database.session.add(user)
    database.session.add(proposal)
    database.session.add(presenter)
    database.session.commit()
    proposal_presenter = ProposalPresenter(proposal.id, presenter.id, proposal, presenter, True)
    proposal.presenters.append(proposal_presenter)
    presenter.proposals.append(proposal_presenter)
    database.session.add(proposal_presenter)
    score = Score(proposal, user, 10)
    comment = Comment(proposal, user, 'Perfect')
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
