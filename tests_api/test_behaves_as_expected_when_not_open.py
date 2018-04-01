"""
Tests ensuring that when the schedule API is not available all routes redirect to the index page.
"""

#  Apparently unused but loading has crucial side effects
import configure

from accuconf import app

# PyCharm fails to spot the use of a fixture.
from test_utils.fixtures import client
from test_utils.functions import get_and_check_content


def test_api_open_index(client, monkeypatch):
    monkeypatch.setitem(app.config, 'API_ACCESS', True)
    get_and_check_content(client, '/', 200, ('ACCU', 'API Access Is Available',))


def test_api_not_open_index(client, monkeypatch):
    get_and_check_content(client, '/', 200, ('ACCU', 'API Access Is Not Available',))


def test_api_not_open_presentations(client, monkeypatch):
    get_and_check_content(client, '/sessions', 302, ('Redirect', '<a href="/">',))


def test_api_not_open_presenters(client, monkeypatch):
    get_and_check_content(client, '/presenters', 302, ('Redirect', '<a href="/">',))
