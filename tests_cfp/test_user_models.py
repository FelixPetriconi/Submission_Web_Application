"""
Test putting an instance the User model into the database and getting it out again.
"""

# PyCharm reports this as unused, but it isn't., it's a fixture
from configure import database

from models.user import User

user_data = (
    'a@b.c',
    'passphrase',
    'User Name',
    '+01234567890',
    'Some Country',
    'Some State',
    'Postcode',
    'Town or City',
    'Street Address',
)


def test_user_in_database(database):
    u = User(*user_data)
    database.session.add(u)
    database.session.commit()
    query_result = User.query.filter_by(email=u.email).all()
    assert len(query_result) == 1
    assert query_result[0] == u
