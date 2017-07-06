from accuconf_cfp import db

from accuconf_cfp.utils.roles import Role


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(512), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False)
    phone = db.Column(db.String(18), nullable=False)
    country = db.Column(db.String(5), nullable=False)
    state = db.Column(db.String(10), nullable=True)
    postal_code = db.Column(db.String(40), nullable=False)
    town_city = db.Column(db.String(30), nullable=False)
    street_address = db.Column(db.String(128), nullable=False)
    proposals = db.relationship('Proposal', back_populates='proposer')
    scores = db.relationship('Score', backref='scorer')
    comments = db.relationship('Comment', backref='commenter')

    def __init__(self, email, password, name, phone, country, state, postal_code, town_city, street_address):
        self.email = email
        self.password = password
        self.name = name
        self.role = Role.user
        self.phone = phone
        self.country = country
        self.state = state
        self.postal_code = postal_code
        self.town_city = town_city
        self.street_address = street_address
