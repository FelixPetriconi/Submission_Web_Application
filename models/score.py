"""SQLAlchemy model classes for reviewing proposals."""

#  The accuconf name is created as an alias for the application package at run time.
from accuconf import db


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'))
    scorer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    proposal = db.relationship('Proposal', back_populates='scores')
    scorer = db.relationship('User', back_populates='scores')
    score = db.Column(db.Integer)

    def __init__(self, proposal, scorer, score):
        self.proposal = proposal
        self.scorer = scorer
        self.score = score


class CommentForProposer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'))
    commenter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    proposal = db.relationship('Proposal', back_populates='comments_for_proposer')
    commenter = db.relationship('User', back_populates='comments_for_proposer')
    comment = db.Column(db.Text)

    def __init__(self, proposal, commenter, comment):
        self.proposal = proposal
        self.commenter = commenter
        self.comment = comment


class CommentForCommittee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    proposal_id = db.Column(db.Integer, db.ForeignKey('proposal.id'))
    commenter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    proposal = db.relationship('Proposal', back_populates='comments_for_committee')
    commenter = db.relationship('User', back_populates='comments_for_committee')
    comment = db.Column(db.Text)

    def __init__(self, proposal, commenter, comment):
        self.proposal = proposal
        self.commenter = commenter
        self.comment = comment
