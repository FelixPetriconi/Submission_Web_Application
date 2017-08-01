import sys

import pycountry

from flask import Flask
# from flask_bootstrap import Bootstrap
from flask_nav import Nav
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

# The packages shared between accucon_cfp and accuconf_api use accuconf as the
#  name of the application package.  Must set this up here in an application
#  specific way. Don't use a proper DI for now, just use this (possibly
#  fragile) hack.
sys.modules['accuconf'] = sys.modules['accuconf_cfp']

countries = {country.name: country.alpha_3 for country in pycountry.countries}

from accuconf_cfp.utils import top_nav

nav = Nav()
nav.register_element('top_nav', top_nav)
nav.init_app(app)

# Only now bring in the views since they likely rely on some of the setup above.
# Ignore the violations of PEP-8.
from accuconf_cfp.views.index import index
from accuconf_cfp.views.register import register
from accuconf_cfp.views.login import login, logout
from accuconf_cfp.views.submit import submit


