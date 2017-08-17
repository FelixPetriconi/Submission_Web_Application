"""
Test putting an instance the User model into the database and getting it out again.
"""

import pytest

# Apparently unused but has required side effects.
import configure

# PyCharm doesn't notice the use as a fixture.
from test_utils.fixtures import database, registrant

from models.user import User


@pytest.mark.parametrize('user_data', (
    # A user with all fields set.
    registrant(),
    # A user with only the mandatory fields set, relying on the defaults
    # for the missing fields.
    {
        'email': 'a@b.c',
        'passphrase': 'Some pass phrase or other.',
        'name': 'User Name',
        'country': 'Some Country',
        'postal_code': 'Postcode',
        'town_city': 'Town or City',
        'street_address': 'Street Address',
    }))
def test_putting_user_data_into_database(user_data, database):
    """Ensure that we can put a user with no proposals or other data into the database.

    Having users with proposals, scores and comments comes later,
    this is simulating registration activity in the database.
    """
    u = User(**user_data)
    database.session.add(u)
    database.session.commit()
    query_result = User.query.filter_by(email=u.email).all()
    assert len(query_result) == 1
    assert query_result[0] == u
