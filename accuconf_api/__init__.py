import sys

from flask import Flask, jsonify, redirect, render_template
from flask_cors import cross_origin
from flask_nav import Nav
from flask_nav.elements import Navbar
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

db = SQLAlchemy(app)

nav = Nav()
nav.register_element('top_nav', Navbar(''))
nav.init_app(app)

# The shared packages use accuconf as the name of the application package.
# must set this up. Don't use a proper DI for now, just use this (possibly
# fragile) hack.
#
# NB Some of these imports rely on accuconf.app and accuconf.db so they must
# be included after the definition of those symbols.
sys.modules['accuconf'] = sys.modules['accuconf_api']
# Not apparently used but has to be loaded, and here is good.
from models.user import User
from models.proposal import Presenter, Proposal


@app.route('/')
def index():
    page = {
        'year': year,
    }
    if app.config['API_ACCESS']:
        return render_template('open_home.html', page=page)
    return render_template('not_open.html', page=page)


def presentation_to_json(presentation):
    result = {
        'id': presentation.id,
        'title': presentation.title,
        'text': presentation.text,
        'day': presentation.day.value,
        'session': presentation.session.value,
        'room': presentation.room.value,
        # 'track': presentation.track.value,
        'presenters': [
            presenter.presenter.id
            for presenter in presentation.presenters
        ]
    }
    if presentation.quickie_slot:
        result['quickie_slot'] = presentation.quickie_slot.value
    return result


def presenter_to_json(presenter):
    return {
        'id': presenter.id,
        'last_name': presenter.last_name,
        'first_name': presenter.first_name,
        'bio': presenter.bio,
        'country': presenter.country,
        'state': presenter.state
    }


def scheduled_presentations():
    return Proposal.query.filter(Proposal.day is not None, Proposal.session is not None).all()


@app.route("/presentations", methods=['GET'])
@cross_origin()
def scheduled_presentations_view():
    if not app.config['API_ACCESS']:
        return redirect('/')
    prop_info = [
        presentation_to_json(prop)
        for prop in scheduled_presentations()
    ]
    return jsonify(prop_info)


@app.route("/presenters", methods=["GET"])
@cross_origin()
def schedule_presenters_view():
    if not app.config['API_ACCESS']:
        return redirect('/')
    scheduled_presenter_ids = {
        presenter.presenter.id
        for prop in scheduled_presentations()
        for presenter in prop.presenters
    }
    json = [
        presenter_to_json(presenter)
        for presenter in Presenter.query.all()
        if presenter.id in scheduled_presenter_ids
    ]
    return jsonify(json)
