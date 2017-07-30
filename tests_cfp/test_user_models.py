"""
Test putting an instance the User model into the database and getting it out again.
"""

import pytest

# Apparently unused but has required side effects.
import configure

# PyCharm doesn't notice the use as a fixture.
from test_utils.fixtures import database

from models.user import User


@pytest.mark.parametrize('user_data', (
    {
        'email': 'a@b.c',
        'passphrase': 'passphrase',
        'name': 'User Name',
        'country': 'Some Country',
        'state': 'Some State',
        'postalcode': 'Postcode',
        'towncity': 'Town or City',
        'address': 'Street Address',
        'phone': '+01234567890',
    },
    {
        'email': 'a@b.c',
        'passphrase': 'passphrase',
        'name': 'User Name',
        'country': 'Some Country',
        'state': None,
        'postalcode': 'Postcode',
        'towncity': 'Town or City',
        'address': 'Street Address',
    }))
def test_user_in_database(user_data, database):
    u = User(*user_data)
    database.session.add(u)
    database.session.commit()
    query_result = User.query.filter_by(email=u.email).all()
    assert len(query_result) == 1
    assert query_result[0] == u
