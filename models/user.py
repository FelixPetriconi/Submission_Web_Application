"""SQLAlchemy model class for users."""

#  The accuconf name is created as an alias for the application package at run time.
from accuconf import db

from models.role_types import Role


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    passphrase = db.Column(db.String(400), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)
    country = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(18), nullable=True)  # ITU E.165 limits numbers to 15 digits
    proposals = db.relationship('Proposal', back_populates='proposer')
    scores = db.relationship('Score', back_populates='scorer')
    comments_for_proposer = db.relationship('CommentForProposer', back_populates='commenter')
    comments_for_committee = db.relationship('CommentForCommittee', back_populates='commenter')

    def __init__(self, email, passphrase, name, country, phone=None, role=Role.user):
        self.email = email
        self.passphrase = passphrase
        self.name = name
        self.role = role
        self.country = country
        self.phone = phone
