"""SQLAlchemy model classes associated with proposals and their presenters."""

from sqlalchemy.ext.associationproxy import association_proxy

#  The accuconf name is created as an alias for the application package at run time.
from accuconf import db

from models.proposal_types import SessionType, ProposalState, SessionAudience
from models.schedule_types import ConferenceDay, SessionSlot, QuickieSlot, Room


class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    proposer = db.relationship('User', back_populates='proposals')
    title = db.Column(db.String(150), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    session_type = db.Column(db.Enum(SessionType), nullable=False)
    audience = db.Column(db.Enum(SessionAudience), nullable=False)
    keywords = db.Column(db.String(100), nullable=True)
    no_video =db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    constraints = db.Column(db.Text, nullable=True)
    status = db.Column(db.Enum(ProposalState), nullable=False)
    # day, session, quickie_slot, track, room, slides_pdf, video_url are only non empty
    # when status is accepted.
    day = db.Column(db.Enum(ConferenceDay))
    session = db.Column(db.Enum(SessionSlot))
    quickie_slot = db.Column(db.Enum(QuickieSlot)) # Only not empty if session_type == quickie.
    room = db.Column(db.Enum(Room))
    presenters = association_proxy('proposal_presenters', 'presenter')
    scores = db.relationship('Score', back_populates='proposal')
    comments_for_proposer = db.relationship('CommentForProposer', back_populates='proposal')
    comments_for_committee = db.relationship('CommentForCommittee', back_populates='proposal')

    def __init__(self, proposer, title, summary, session_type, audience=SessionAudience.all,
                 keywords='', no_video=False, notes='', constraints='', status=ProposalState.submitted,
                 day=None, session=None, quickie_slot=None, room=None):
        self.proposer = proposer
        self.title = title
        self.summary = summary
        self.session_type = session_type
        self.audience = audience
        self.keywords = keywords
        self.no_video = no_video
        self.notes = notes
        self.constraints= constraints
        self.status = status
        self.day = day
        self.session = session
        self.quickie_slot = quickie_slot
        self.room = room


class Presenter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.Text(), nullable=False)
    country = db.Column(db.String(60), nullable=False)
    proposals = association_proxy('presenter_proposals', 'proposal')

    def __init__(self, email, name, bio, country):
        self.email = email
        self.name = name
        self.bio = bio
        self.country = country


class ProposalPresenter(db.Model):
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'), primary_key=True)
    presenter_id = db.Column(db.Integer, db.ForeignKey('presenter.id'), primary_key=True)
    proposal = db.relationship(Proposal, backref='proposal_presenters')
    presenter = db.relationship(Presenter, backref='presenter_proposals')
    is_lead = db.Column(db.Boolean, nullable=False)

    def __init__(self, proposal, presenter, is_lead):
        self.proposal = proposal
        self.presenter = presenter
        self.is_lead = is_lead
