"""SQLAlchemy model classes associated with proposals and their presenters."""

from sqlalchemy.ext.associationproxy import association_proxy

#  The accuconf name is created as an alias for the application package at run time.
from accuconf import db

from models.proposal_types import SessionType, SessionCategory, ProposalState, SessionAudience
from models.schedule_types import ConferenceDay, SessionSlot, QuickieSlot, Track, Room


class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    proposer = db.relationship('User', back_populates='proposals')
    title = db.Column(db.String(150), nullable=False)
    session_type = db.Column(db.Enum(SessionType), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    constraints = db.Column(db.Text, nullable=True)
    presenters = association_proxy('proposal_presenters', 'presenter')
    audience = db.Column(db.Enum(SessionAudience), nullable=False)
    # category = db.Column(db.Enum(SessionCategory), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    scores = db.relationship('Score', back_populates='proposal')
    comments = db.relationship('Comment', back_populates='proposal')
    status = db.Column(db.Enum(ProposalState), nullable=False)
    # day, session, quickie_slot, track, room, slides_pdf, video_url are only non empty
    # when status is accepted.
    day = db.Column(db.Enum(ConferenceDay))
    session = db.Column(db.Enum(SessionSlot))
    quickie_slot = db.Column(db.Enum(QuickieSlot)) # Only not empty if session_type == quickie.
    track = db.Column(db.Enum(Track))
    room = db.Column(db.Enum(Room))
    # slides_pdf and video_url can only be completed after the conference.
    slides_pdf = db.Column(db.String(100))
    video_url = db.Column(db.String(100))

    def __init__(self, proposer, title, session_type, summary, notes='', constraints='',
                 audience=SessionAudience.all, category='', status=ProposalState.submitted,
                 day=None, session=None, quickie_slot=None, track=None, room=None,
                 slides_pdf=None, video_url=None):
        self.proposer = proposer
        self.title = title
        self.session_type = session_type
        self.summary = summary
        self.notes = notes
        self.constraints = constraints
        self.audience = audience
        self.category = category
        self.status = status
        self.day = day
        self.session = session
        self.quickie_slot = quickie_slot
        self.track = track
        self.room = room
        self.slides_pdf = slides_pdf
        self.video_url = video_url


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
