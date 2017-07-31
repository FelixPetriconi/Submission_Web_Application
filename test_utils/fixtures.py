"""
Various fixtures used in various testing places.
"""

import pytest

from accuconf import app, db


@pytest.fixture
def database():
    """Deliver up the database associated with the application.

    Whatever the location of the database for the current configuration,
    override it for the tests.
    """
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield db
        db.session.rollback()
        db.drop_all()


@pytest.fixture()
def client():
    """A Werkzeug client in testing mode with a newly created database.
    """
    app.config['TESTING'] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()
        db.session.rollback()
        db.drop_all()
