import hashlib
import random
import sys

import pycountry

from flask import Flask, jsonify, redirect, render_template, request, session
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

# The shared packages use accuconf as the name of the application package.
# must set this up. Don't use a proper DI for now, just use this (possibly
# fragile) hack.
#
# NB Some of these imports rely on accuconf.app and accuconf.db so they must
# be included after the definition of those symbols.
sys.modules['accuconf'] = sys.modules['accuconf_cfp']
from models.user import User
from models.proposal import Proposal, ProposalPresenter, Presenter, SessionType
from utils.validator import is_valid_new_email, validate_proposal_data

countries = {country.name: country.alpha_3 for country in pycountry.countries}


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


nav = Nav()
nav.register_element('top_nav', top_nav)
nav.init_app(app)


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


@app.route('/')
def index():
    page = {
        'type': 'Index',
        'year': year,
    }
    if app.config['MAINTENANCE']:
        return render_template('maintenance.html', page=page)
    if not (app.config['CALL_OPEN'] or app.config['REVIEWING_ALLOWED']):
        return render_template('not_open.html', page=page)
    return render_template('open_home.html', page=page)


@app.route('/register', methods=['GET', 'POST'])
def register():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    user = None
    if is_logged_in():
        user = User.query.filter_by(email=session['email']).first()
    edit_mode = bool(user)
    page = {
        'type': 'Registration',
        'year': year,
    }
    if request.method == 'POST':
        email = request.form['email'].strip()
        passphrase = request.form['passphrase'].strip()
        cpassphrase = request.form['cpassphrase'].strip()
        name = request.form['name'].strip()
        phone = request.form['phone'].strip()
        country = request.form['country'].strip()
        state = request.form['state'].strip()
        postal_code = request.form['postalcode'].strip()
        town_city = request.form['towncity'].strip()
        street_address = request.form['streetaddress'].strip()

        # TODO Probably should not check passphrases this way for logged in situation.
        if passphrase:
            if not cpassphrase:
                return render_template('failure.html', page=md(page, {'data': 'Passphrase given but no confirmation passphrase'}))
            if passphrase != cpassphrase:
                return render_template('failure.html', page=md(page, {'data': 'Passphrase and confirmation passphrase dffer.'}))
            encoded_passphrase = hashlib.sha256(passphrase.encode('utf-8')).hexdigest()
        else:
            if cpassphrase:
                return render_template('failure.html', page=md(page, {'data': 'No passphrase given but even though confirmation passphrase given.'}))
            return render_template('failure.html', page=md(page, {'data': 'Neither passphrase nor confirmation passphrase entered.'}))

        if edit_mode:
            User.query.filter_by(email=email).update({
                'email': email,
                'name': name,
                'phone': phone,
                'country': country,
                'state': state,
                'postal_code': postal_code,
                'town_city': town_city,
                'street_address': street_address
            })
            if encoded_passphrase:
                user.passphrase = encoded_passphrase
                User.query.filter_by(email=user.email).update({'passphrase': encoded_passphrase})
            return render_template('success.html', page=md(page, {'data': 'Your account details were successful updated.'}))
        else:
            if not is_valid_new_email(email):
                return render_template("failure.html", page=md(page, {'data': '''The email address was either invalid or already in use.
Please register again.'''}))
            errors = [
                field_name
                for field, field_name in (
                    (email, 'email'),
                    (passphrase, 'passphrase'),
                    (cpassphrase, 'passphrase confirmation'),
                    (name, 'name'),
                    (town_city, 'town/city'),
                    (phone, 'phone number'),
                    (postal_code, 'postal code'),
                    (street_address, 'street address'),)
                if not field.strip()
            ]
            if errors:
                return render_template("failure.html", page=md(page, {'data': '''The fields:
{}
 were not completed.

 Please register again.'''.format(' ,'.join(errors))}))
            db.session.add(User(
                email,
                encoded_passphrase,
                name,
                phone,
                country,
                state,
                postal_code,
                town_city,
                street_address,
            ))
        db.session.commit()
        return render_template("success.html", page={'type': 'Registration', 'data': '''You have successfully registered for submitting
proposals for the ACCU Conf. Please login and
start preparing your proposal for the conference.'''})
    else:
        num_a = random.randint(10, 99)
        num_b = random.randint(10, 99)
        return render_template("register.html", page=md(page, {
            'email': user.email if edit_mode else '',
            'name': user.name if edit_mode else '',
            'phone': user.phone if edit_mode else '',
            'country': user.country if edit_mode else 'GBR',  # UK shall be the default
            'state': user.state if edit_mode else '',
            'postal_code': user.postal_code if edit_mode else '',
            'town_city': user.town_city if edit_mode else '',
            'street_address': user.street_address if edit_mode else '',
            'title': 'Account Information' if edit_mode else 'Register',
            'data': 'Here you can edit your account information' if edit_mode else 'Register here for submitting proposals to ACCU Conference',
            'puzzle': '{} + {}'.format(num_a, num_b),
            'submit_button': 'Save' if edit_mode else 'Register',
            'countries': list(countries.keys()),
        }))


@app.route('/login', methods=['GET', 'POST'])
def login():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    page = {
        'type': 'Login',
        'year': year,
    }
    if request.method == 'POST':
        email = request.form['email']
        passphrase = request.form['passphrase']
        user = User.query.filter_by(email=email).first()
        if not user:
            return render_template('failure.html', page=md(page, {'data': 'Login was not successful.'}))
        passphrase_hash = hashlib.sha256(passphrase.encode("utf-8")).hexdigest()
        if user.passphrase == passphrase_hash:
            session['email'] = user.email
            #  TODO  Change something so as to see the login state. Menu changes of course.
            return redirect('/')
        else:
            return render_template('failure.html', page=md(page, {'data': 'Login was not successful.'}))
    else:
        return render_template('login.html', page=page)


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    page = {
        'title': 'Submit',
        'year': year,
    }
    if is_logged_in():
        if request.method == 'POST':
            user = User.query.filter_by(email=session['email']).first()
            if user:
                proposal_data = request.json
                status, message = validate_proposal_data(proposal_data)
                response = {}
                if status:
                    proposal = Proposal(
                        user,
                        proposal_data.get('title').strip(),
                        SessionType(proposal_data.get('session_type')),
                        proposal_data.get('abstract').strip()
                    )
                    db.session.add(proposal)
                    presenters_data = proposal_data.get('presenters')
                    for presenter_data in presenters_data:
                        presenter = Presenter(
                            presenter_data['email'],
                            presenter_data['name'],
                            'A human being.',
                            presenter_data['country'],
                            presenter_data['state'],
                        )
                        ProposalPresenter(proposal, presenter, presenter_data['lead'])
                        db.session.add(presenter)
                    db.session.commit()
                    response['success'] = True
                    response['message'] = '''Thank you, you have successfully submitted a proposal for the ACCU {} conference!
If you need to edit it you can via the 'My Proposal' menu item.'''.format(year)
                    response['redirect'] = '/'
                else:
                    response['success'] = False
                    response['message'] = message
                return jsonify(**response)
        else:
            user = User.query.filter_by(email=session['email']).first()
            if user:
                return render_template('submit.html', page={
                    'title': 'Submit a proposal for ACCU {}'.format(year),
                    'name': user.name,
                    'proposer': {
                        'email': user.email,
                        'name': user.name,
                        'bio': 'A human being.',
                        'country': user.country,
                        'state': user.state,
                    }
                })
    return render_template('failure.html', page=md(page, {'data': 'Must be logged in to submit a proposal.'}))
