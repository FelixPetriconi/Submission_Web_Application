import sys

from flask import Flask, jsonify, redirect, render_template
from flask_cors import cross_origin
from flask_nav import Nav
from flask_nav.elements import Navbar
from flask_sqlalchemy import SQLAlchemy

try:
    from accuconf_api_config import Config
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
# Not apparently used but they have to be loaded, and here is good.
from models.user import User
from models.score import Score
from models.proposal import Presenter, Proposal


@app.route('/')
def index():
    if app.config['API_ACCESS']:
        return render_template('general.html', page={
            'pagetitle': 'API Access Is Available',
            'year': year,
            'data': 'The ACCU {} API access to the schedule information is currently available.'.format(year),
        })
    return render_template('general.html', page={
        'pagetitle': 'API Access Is Not Available',
        'year': year,
        'data': 'The ACCU {} API is not available at this time.'.format(year),
    })


def session_to_json(session):
    result = {
        'id': session.id,
        'title': session.title,
        'summary': session.summary,
        'day': session.day.value,
        'session': session.session.value,
        'room': session.room.value,
        # 'track': presentation.track.value,
        'presenters': [
            presenter.id
            for presenter in session.presenters
        ]
    }
    if session.quickie_slot:
        result['quickie_slot'] = session.quickie_slot.value
    return result


def presenter_to_json(presenter):
    return {
        'id': presenter.id,
        'name': presenter.name,
        'bio': presenter.bio,
        'country': presenter.country,
    }


def scheduled_sessions():
    # TODO Why does this query return all the proposals not just the scheduled ones?
    # return Proposal.query.filter(Proposal.day is not None, Proposal.session is not None).all()
    return [
        proposal
        for proposal in Proposal.query.all()
        if proposal.day is not None  and proposal.session is not None
    ]


@app.route("/sessions", methods=['GET'])
@cross_origin()
def sessions_view():
    if not app.config['API_ACCESS']:
        return redirect('/')
    prop_info = [
        session_to_json(prop)
        for prop in scheduled_sessions()
    ]
    return jsonify(prop_info)


@app.route("/presenters", methods=["GET"])
@cross_origin()
def presenters_view():
    if not app.config['API_ACCESS']:
        return redirect('/')
    scheduled_presenter_ids = {
        presenter.id
        for prop in scheduled_sessions()
        for presenter in prop.presenters
    }
    json = [
        presenter_to_json(presenter)
        for presenter in Presenter.query.all()
        if presenter.id in scheduled_presenter_ids
    ]
    return jsonify(json)
