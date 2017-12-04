"""
This tests that the Werkzeug test client of the application is accessible,
and that each route delivers up a page with some expected content without
any unexpected content.
"""

# Apparently unused but loading has crucial side effects
import configure

from accuconf_cfp import app

from test_utils.constants import login_menu_item, register_menu_item
# PyCharm fails to spot the use of this symbol as a fixture.
from test_utils.fixtures import client
from test_utils.functions import get_and_check_content

#  NB The word Register is almost certain to appear in the template.


def test_top_page_not_open(client):
    get_and_check_content(client, '/', 200, ('ACCU', 'is not open'), ('Login', 'Maintenance',))


def test_register_page_not_open(client):
    get_and_check_content(client, '/register', 302, ('Redirecting', 'href="/"'))


def test_register_success_page_not_open(client):
    get_and_check_content(client, '/register_success', 302, ('Redirecting', 'href="/"'))


def test_registration_update_page_not_open(client):
    get_and_check_content(client, '/registration_update', 302, ('Redirecting', 'href="/"'))


def test_registration_update_success_page_not_open(client):
    get_and_check_content(client, '/registration_update_success', 302, ('Redirecting', 'href="/"'))


def test_login_page_not_open(client):
    get_and_check_content(client, '/login', 302, ('Redirecting', 'href="/"'), ())


def test_login_success_page_not_open(client):
    get_and_check_content(client, '/login_success', 302, ('Redirecting', 'href="/"'), ())


def test_logout_page_not_open(client):
    get_and_check_content(client, '/logout', 302, ('Redirecting', 'href="/"'), ())


def test_submit_page_not_open(client):
    get_and_check_content(client, '/submit', 302, ('Redirecting', 'href="/"'), ())


def test_submit_success_page_not_open(client):
    get_and_check_content(client, '/submit_success', 302, ('Redirecting', 'href="/"'), ())


def test_my_proposals_page_not_open(client):
    get_and_check_content(client, '/my_proposals', 302, ('Redirecting', 'href="/"'), ())


def test_proposal_update_page_not_open(client):
    get_and_check_content(client, '/proposal_update/1', 302, ('Redirecting', 'href="/"'), ())


def test_proposal_update_success_page_not_open(client):
    get_and_check_content(client, '/proposal_update_success', 302, ('Redirecting', 'href="/"'), ())


def test_review_list_page_not_open(client):
    get_and_check_content(client, '/review_list', 302, ('Redirecting', 'href="/"'), ())


def test_review_proposal_page_not_open(client):
    get_and_check_content(client, '/review_proposal/1', 302, ('Redirecting', 'href="/"'), ())


def test_top_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/', 200, ('ACCU', 'Register', 'Login'), ('Maintenance',))


def test_register_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/register', 200, ('ACCU', 'Register'), ('Maintenance',))


def test_register_success_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/register_success', 302, ('Redirecting', 'href="/"'))


def test_registration_update_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/registration_update', 302, ('Redirecting', 'href="/"'))


def test_registration_update_success_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/registration_update_success', 302, ('Redirecting', 'href="/"'))


def test_login_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/login', 200, ('ACCU', 'Login'), ('Maintenance',))


def test_login_success_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/login_success', 302, ('Redirecting', 'href="/"'), ())


def test_logout_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/logout', 302, ('Redirecting', 'href="/"'), ())


def test_submit_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/submit', 200, (' – Submit',), ())


def test_submit_success_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/submit_success', 200, (' – Submit Failed', login_menu_item, register_menu_item), ())


def test_my_proposals_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/my_proposals', 200, ('– My Proposals Failure',), ())


def test_proposal_update_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/proposal_update/1', 200, (' – Proposal Update Failure',), ())


def test_proposal_update_success_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/proposal_update_success', 200, (' – Update Failed', login_menu_item, register_menu_item), ())


def test_review_list_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL_OPEN', True)
    get_and_check_content(client, '/review_list', 200, (' – Review List Failed', login_menu_item, register_menu_item), ())


def test_review_list_page_call_closed_reviewing_allowed(client, monkeypatch):
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', True)
    get_and_check_content(client, '/review_list', 302, ('Redirecting', 'href="/"'), ())


def test_review_proposal_page_call_open(client, monkeypatch):
    monkeypatch.setitem(app.config, 'CALL OPEN', True)
    get_and_check_content(client, '/review_proposal/1', 302, ('Redirecting', 'href="/"'), ())


def test_review_proposal_page_call_closed_reviewing_allowed(client, monkeypatch):
    monkeypatch.setitem(app.config, 'REVIEWING_ALLOWED', True)
    get_and_check_content(client, '/review_proposal/1', 302, ('Redirecting', 'href="/"'), ())


def test_top_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/', 200, ('ACCU', 'undergoing maintenance'), ('Login',))


def test_register_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/register', 302, ('Redirecting', 'href="/"'))


def test_register_success_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/register_success', 302, ('Redirecting', 'href="/"'))


def test_registration_update_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/registration_update', 302, ('Redirecting', 'href="/"'))


def test_registration_update_success_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/registration_update_success', 302, ('Redirecting', 'href="/"'))


def test_login_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/login', 302, ('Redirecting', 'href="/"'), ())


def test_login_success_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/login_success', 302, ('Redirecting', 'href="/"'), ())


def test_logout_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/logout', 302, ('Redirecting', 'href="/"'), ())


def test_submit_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/submit', 302, ('Redirecting', 'href="/"'), ())


def test_submit_success_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/submit_success', 302, ('Redirecting', 'href="/"'), ())


def test_my_proposals_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/my_proposals', 302, ('Redirecting', 'href="/"'), ())


def test_proposal_update_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/proposal_update/1', 302, ('Redirecting', 'href="/"'), ())


def test_proposal_update_success_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/proposal_update_success', 302, ('Redirecting', 'href="/"'), ())


def test_review_list_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/review_list', 302, ('Redirecting', 'href="/"'), ())


def test_review_proposal_page_maintenance(client, monkeypatch):
    monkeypatch.setitem(app.config, 'MAINTENANCE', True)
    get_and_check_content(client, '/review_proposal/1', 302, ('Redirecting', 'href="/"'), ())
