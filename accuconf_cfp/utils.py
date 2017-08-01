"""Various utility functions.

A collection of functions used by various route controllers. The route controllers
are in separate modules hence pulling these functions out into a separate module.
"""

import re

from flask import redirect, session

from accuconf_cfp import app

from models.user import User


def is_logged_in():
    """Predicate to determine if a user is logged in.

    On logging in a record is placed into the session data structure with key 'email'.
    The record is removed on logout.
    """
    return 'email' in session and session['email']


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


def is_valid_new_email(email):
    """Proposed new email is valide format and not already in use."""
    email_pattern = re.compile("^([a-zA-Z0-9_.+-])+@(([a-zA-Z0-9-_])+\.)+([a-zA-Z0-9])+$")
    if email_pattern.search(email):
        return not User.query.filter_by(email=email).first()
    else:
        return False


def validate_proposal_data(proposal_data):
    """Proposal data is not invalid."""
    mandatory_keys = ["title", "abstract", "session_type", "presenters"]
    for key in mandatory_keys:
        if key not in proposal_data:
            return False, "{} information is not present in proposal".format(key)

        if proposal_data[key] is None:
            return False, "{} information should not be empty".format(key)
    if type(proposal_data["presenters"]) != list:
        return False, "presenters data is malformed"

    if len(proposal_data["presenters"]) < 1:
        return False, "At least one presenter needed"

    if len(proposal_data.get("title")) < 5:
        return False, "Title is too short"

    if len(proposal_data.get("abstract")) < 50:
        return False, "Proposal too short"

    (result, message) = validate_presenters(proposal_data["presenters"])
    if not result:
        return result, message

    return True, "validated"


def validate_presenters(presenters):
    """Presenter data is not invalid."""
    mandatory_keys = ["lead", "email", "fname", "lname", "country", "state"]
    lead_found = False
    lead_presenter = ""
    for presenter in presenters:
        for key in mandatory_keys:
            if key not in presenter:
                return False, "{} attribute is mandatory for Presenters".format(key)

            if presenter[key] is None:
                return False, "{} attribute should have valid data".format(key)

        if "lead" in presenter and "email" in presenter:
            if presenter["lead"] and lead_found:
                return False, "{} and {} are both marked as lead presenters".format(presenter["email"], lead_presenter)
            elif presenter["lead"] and not lead_found:
                lead_found = True
                lead_presenter = presenter["email"]

    return True, "validated"
