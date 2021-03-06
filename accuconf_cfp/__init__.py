"""The driver of the ACCUConf CFP Web application.

Define various symbols that everything depends on here. All the route controllers
and various utilities are defined in other modules.
"""
import sys

import pycountry

from flask import Flask, request, session
# from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View

from flask_sqlalchemy import SQLAlchemy

try:
    from accuconf_cfp_config import Config
except ImportError:
    from models.configuration import Config

year = 2019

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']
app.logger.info(app.url_map)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# Bootstrap(app)
db = SQLAlchemy(app)

# The packages shared between accuconf_cfp and accuconf_api use accuconf as the
#  name of the application package.  Must set this up here in an application
#  specific way. Don't use a proper DI for now, just use this (possibly
#  fragile) hack.
sys.modules['accuconf'] = sys.modules['accuconf_cfp']

# A set  of all the countries currently known.
countries = {country.name for country in pycountry.countries}

# This include require app to be already defined in this module.
from accuconf_cfp.utils import is_logged_in

from models.user import User
from models.role_types import Role


def top_nav():
    """The callable that delivers the left-side menu for the current state ."""
    if app.config['MAINTENANCE']:
        return Navbar('')
    if not (app.config['CALL_OPEN'] or app.config['REVIEWING_ALLOWED']):
        return Navbar('')
    logged_in = is_logged_in()
    entries = []
    if app.config['CALL_OPEN'] and not logged_in and request.path != '/register':
        entries.append(View('Register', 'register'))
    if not logged_in and request.path != '/login':
        entries.append(View('Login', 'login'))
    if app.config['CALL_OPEN'] and logged_in and request.path != '/submit':
        entries.append(View('Submit a Proposal', 'submit'))
    if logged_in and request.path != '/registration_update':
        entries.append(View('Registration Update', 'registration_update'))
    if app.config['CALL_OPEN'] and logged_in and request.path != '/my_proposals':
        entries.append(View('My Proposals', 'my_proposals'))
    if app.config['REVIEWING_ALLOWED'] and logged_in and request.path != '/review_list':
        user = User.query.filter_by(email=session['email']).first()
        if user and user.role == Role.reviewer:
            entries.append(View('Review Proposals', 'review_list'))
    if logged_in:
        entries.append(View('Logout', 'logout'))
    return Navbar('', *entries)


nav = Nav()
nav.register_element('top_nav', top_nav)
nav.init_app(app)

# Only now bring in the views since they likely rely on some of the setup above.
# Ignore the violations of PEP-8.
import accuconf_cfp.views.index
import accuconf_cfp.views.register
import accuconf_cfp.views.login
import accuconf_cfp.views.submit
import accuconf_cfp.views.review


