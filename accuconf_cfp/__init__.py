"""The driver of the ACCUConf CFP Web application.

Define various symbols that everything depends on here. All the route controllers
and various utilities are defined in other modules.
"""
import sys

import pycountry

from flask import Flask, request
# from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View

from flask_sqlalchemy import SQLAlchemy

try:
    from accuconf_config import Config
except ImportError:
    from models.configuration import Config

year = 2018

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']
app.logger.info(app.url_map)

# Bootstrap(app)
db = SQLAlchemy(app)

# The packages shared between accuconf_cfp and accuconf_api use accuconf as the
#  name of the application package.  Must set this up here in an application
#  specific way. Don't use a proper DI for now, just use this (possibly
#  fragile) hack.
sys.modules['accuconf'] = sys.modules['accuconf_cfp']

# A dictionary mapping known country names as displayed in forms to their official
# three letter form.
countries = {country.name: country.alpha_3 for country in pycountry.countries}

# This include require app to be already defined in this module.
from accuconf_cfp.utils import is_logged_in


def top_nav():
    """The callable that delivers the left-side menu for the current state ."""
    if app.config['MAINTENANCE']:
        return Navbar('')
    if not (app.config['CALL_OPEN'] or app.config['REVIEWING_ALLOWED']):
        return Navbar('')
    logged_in = is_logged_in()
    entries = []
    if not logged_in and request.path != '/register':
        entries.append(View('Register', 'register'))
    if not logged_in and request.path != '/login':
        entries.append(View('Login', 'login'))
    if app.config['CALL_OPEN'] and logged_in and request.path != '/submit':
        entries.append(View('Submit a Proposal', 'submit'))
    if logged_in and request.path != '/registration_update':
        entries.append(View('Registration Update', 'registration_update'))
    if app.config['CALL_OPEN'] and logged_in and request.path != '/my_proposals':
        entries.append(View('My Proposals', 'my_proposals'))
    if logged_in:
        entries.append(View('Logout', 'logout'))
    return Navbar('', *entries)


nav = Nav()
nav.register_element('top_nav', top_nav)
nav.init_app(app)

# Only now bring in the views since they likely rely on some of the setup above.
# Ignore the violations of PEP-8.
from accuconf_cfp.views.index import index
from accuconf_cfp.views.register import register
from accuconf_cfp.views.login import login, logout
from accuconf_cfp.views.submit import submit


