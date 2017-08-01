from flask import redirect, request, session
from flask_nav.elements import Navbar, View

from accuconf_cfp import app


def is_logged_in():
    """Predicate to determine if a user is logged in.

    On logging in a record is placed into the session data structure with key 'email'.
    The record is removed on logout.
    """
    return 'email' in session and session['email']


def top_nav():
    """The callable that delivers the left-side menu for the current state ."""
    if app.config['MAINTENANCE']:
        return Navbar('')
    logged_in = is_logged_in()
    entries = []
    if app.config['CALL_OPEN'] and not logged_in and request.path != '/register':
        entries.append(View('Register', 'register'))
    if (app.config['CALL_OPEN'] or app.config['REVIEWING_ALLOWED']) and not logged_in and request.path != '/login':
        entries.append(View('Login', 'login'))
    return Navbar('', *entries)


def is_acceptable_route():
    """Check the state of the application and return a pair.

    The first item of the pair is a Boolean stating whether the route is acceptable.
    The second item of the pair is a rendered template to display if the route is not
     allowed, and None if it is.
    """
    if app.config['MAINTENANCE']:
        return (False, redirect('/'))
    if not app.config['CALL_OPEN']:
        if app.config['REVIEWING_ALLOWED']:
            return (True, None)
        return (False, redirect('/'))
    return (True, None)


#  This code has to work on Python 3.4, so cannot use the lovely Python 3.5 and later stuff.
#  Must have the ability to merge two dictionaries, but no 3.5 stuff so this for 3.4.
def md(a, b):
    """Merge two dictionaries into a distinct third one."""
    rv = a.copy()
    rv.update(b)
    return rv



