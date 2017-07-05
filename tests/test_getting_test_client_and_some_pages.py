"""
This tests that we are able to access the Werkzeug test client of the application,
and that each route delivers up a page with some expected content without
any unexpected content.
"""

from common import client, get_and_check_content

import sys
from pathlib import PurePath

path_to_add = str(PurePath(__file__).parent.parent)
if path_to_add not in sys.path:
    sys.path.insert(0, path_to_add)

from accuconf import app

#  NB app is a global variable with only one per test session so back out of any state changes.
#  This is made easy by using the pytest monkeypatch fixture.


def test_the_top_page_closed(client, monkeypatch):
    assert client is not None
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    get_and_check_content(client, '/', 200, ('ACCU', 'not available'), ('Register', 'Login', 'Maintenance',))


def test_the_registration_page_closed(client, monkeypatch):
    assert client is not None
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    get_and_check_content(client, '/register', 200, ('ACCU', 'not available'), ('Register', 'Login', 'Maintenance'))


def test_the_login_page_call_closed(client, monkeypatch):
    assert client is not None
    monkeypatch.setitem(app.config, 'CALL_OPEN', False)
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', False)
    get_and_check_content(client, '/login', 200, ('ACCU', 'not available'), ('Register', 'Login', 'Maintenance'))


def test_the_top_page_call_open(client, monkeypatch):
    assert client is not None
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/', 200, ('ACCU', 'Register', 'Login'), ('Maintenance',))


def test_the_registration_page_call_open(client, monkeypatch):
    assert client is not None
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/register', 200, ('ACCU', 'Register'), ('Login', 'Maintenance'))


def test_the_login_page_call_open(client, monkeypatch):
    assert client is not None
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/login', 200, ('ACCU', 'Login'), ('Register', 'Maintenance'))


def test_the_top_page_maintenance(client, monkeypatch):
    assert client is not None
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/', 200, ('ACCU', 'Maintenance'), ('Register', 'Login'))


def test_the_register_page_maintenance(client, monkeypatch):
    assert client is not None
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/register', 200, ('ACCU', 'Maintenance'), ('Register', 'Login'))


def test_the_login_page_maintenance(client, monkeypatch):
    assert client is not None
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/login', 200, ('ACCU', 'Maintenance'), ('Register', 'Login'))
