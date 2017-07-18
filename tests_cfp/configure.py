"""
Various configurations for a cfp application test..
"""

import pytest
import sys

#  Tests are not always initiated from the top level of the project. Ensure that
# directory is in the path so that imports work.
from pathlib import PurePath

path_to_add = str(PurePath(__file__).parent.parent)
if path_to_add not in sys.path:
    sys.path.insert(0, path_to_add)

# In the context of  a unit test, the symbol accuconf is not defined. Must
# therefore use one of the two applications to provide the database.
from accuconf_cfp import app, db


@pytest.fixture
def database():
    """
    Deliver up the database associated with the application.
    """
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield db
        db.session.rollback()
        db.drop_all()


@pytest.fixture()
def client():
    """
    A Werkzeug client in testing mode with a newly created database.
    """
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()
        db.session.rollback()
        db.drop_all()
