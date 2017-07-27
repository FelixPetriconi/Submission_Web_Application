import hashlib
import random
import sys

from flask import Flask, redirect, render_template, request, session
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
from models.security import MathPuzzle
from utils.validator import is_valid_new_email


def _top_nav():
    """The callable that delivers the left-side menu for the current state ."""
    if app.config['MAINTENANCE']:
        return Navbar('')
    logged_in = 'email' in session and session['email']
    entries = []
    if app.config['CALL_OPEN'] and not logged_in and request.path != '/register':
        entries.append(View('Register', 'register'))
    if (app.config['CALL_OPEN'] or app.config['REVIEWING_ALLOWED']) and not logged_in and request.path != '/login':
        entries.append(View('Login', 'login'))
    return Navbar('', *entries)


nav = Nav()
nav.register_element('top_nav', _top_nav)
nav.init_app(app)


def _is_acceptable_route():
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
#  Must have the ability to merge two dictionaries, but no 3.5 stuff so this.
def _md(a, b):
    """Merge to dictionaries into a distinct third one."""
    rv = a.copy()
    rv.update(b)
    return rv


@app.route('/')
def index():
    page = {'year': year}
    if app.config['MAINTENANCE']:
        return render_template('maintenance.html', page=page)
    if not (app.config['CALL_OPEN'] or app.config['REVIEWING_ALLOWED']):
        return render_template('not_open.html', page=page)
    return render_template('open_home.html', page=page)


@app.route('/register', methods=['GET', 'POST'])
def register():
    check = _is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    edit_mode = False
    user = None
    if session.get("email", False):  # Determines if a user is logged in.
        user = User.query.filter_by(email=session["email"]).first()
        if user is not None:
            edit_mode = True
    page = {
        'type': 'Registration',
        'year': year,
    }
    if request.method == "POST":
        email = request.form["email"].strip()
        passphrase = request.form["passphrase"].strip()
        cpassphrase = request.form["cpassphrase"].strip()
        name = request.form["name"].strip()
        phone = request.form["phone"].strip()
        country = request.form["country"].strip()
        state = request.form["state"].strip()
        postal_code = request.form["postalcode"].strip()
        town_city = request.form['towncity'].strip()
        street_address = request.form['streetaddress'].strip()

        # TODO Probably should not check passphrases this way for logged in situation.
        if passphrase:
            if not cpassphrase:
                return render_template('failure.html', page=_md(page, {'data': 'Passphrase given but no confirmation passphrase'}))
            if passphrase != cpassphrase:
                return render_template('failure.html', page=_md(page, {'data': 'Passphrase and confirmation passphrase dffer.'}))
            encoded_passphrase = hashlib.sha256(passphrase.encode('utf-8')).hexdigest()
        else:
            if cpassphrase:
                return render_template('failure.html', page=_md(page, {'data': 'No passphrase given but even though confirmation passphrase given.'}))
            return render_template('failure.html', page=_md(page, {'data': 'Neither passphrase nor confirmation passphrase entered.'}))

        if edit_mode:
            user.email = email
            user.name = name
            user.phone = phone
            user.country = country
            user.state = state
            user.postal_code = postal_code
            user.town_city = town_city
            user.street_address = street_address
            User.query.filter_by(email=user.email).update({
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
                User.query.filter_by(email=user.email).update({'passphrase': encoded_passphrase })
            return render_template('success.html', page=_md(page, {'data': 'Your account details were successful updated.'}))
        else:
            if not is_valid_new_email(email):
                return render_template("failure.html", page=_md(page, {'data': '''The email address was either invalid or already in use.
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
                return render_template("failure.html", page=_md(page, {'data': '''The fields:
{}
 were not completed.

 Please register again.'''.format(' ,'.join(errors))}))
            else:
                new_user = User(
                    email,
                    encoded_passphrase,
                    name,
                    phone,
                    country,
                    state,
                    postal_code,
                    town_city,
                    street_address,
                )
                db.session.add(new_user)
        db.session.commit()
        return render_template("success.html", page={'type': 'Registration', 'data': '''You have successfully registered for submitting
proposals for the ACCU Conf. Please login and
start preparing your proposal for the conference.'''})
    else:
        num_a = random.randint(10, 99)
        num_b = random.randint(10, 99)
        question = MathPuzzle(num_a + num_b)
        db.session.add(question)
        db.session.commit()
        page = {
            'mode': 'edit_mode' if edit_mode else 'register',
            'email': user.email if edit_mode else '',
            'name': user.name if edit_mode else '',
            'phone': user.phone if edit_mode else '',
            'country': user.country if edit_mode else 'GBR', # UK shall be the default
            'state': user.state if edit_mode else '',
            'postal_code': user.postal_code if edit_mode else '',
            'town_city': user.town_city if edit_mode else '',
            'street_address': user.street_address if edit_mode else '',
            'title': 'Account Information' if edit_mode else 'Register',
            'data': 'Here you can edit your account information' if edit_mode else 'Register here for submitting proposals to ACCU Conference',
            'question': question.id,
            'puzzle': '{} + {}'.format(num_a, num_b),
            'submit_button': 'Save' if edit_mode else 'Register',
        }
        return render_template("register.html", page=page)


@app.route('/login', methods=['GET', 'POST'])
def login():
    check = _is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    if request.method == "POST":
        email = request.form['email']
        passphrase = request.form['passphrase']
        user = User.query.filter_by(email=email).first()
        if not user:
            return render_template('failure.html', page={'type': 'Login', 'year': year, 'data': 'Unknown user/passphrase combination.'})
        passphrase_hash = hashlib.sha256(passphrase.encode("utf-8")).hexdigest()
        if user.passphrase == passphrase_hash:
            session['email'] = user.email
            #  TODO  Change something so as to see the login state. Menu changes of course.
            return redirect('/')
        else:
            return redirect('/login')
    else:
        return render_template("login.html", page={'year': year})


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    check = _is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    if request.method == 'POST':
        pass
    else:
        if session.get('email', False):
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
        return render_template('failure.html', page={'data': 'Must be logged in to submit a proposal.'})
