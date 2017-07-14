import hashlib
import sys

from flask import Flask, redirect, render_template, request, session
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

try:
    from accuconf_config import Config
except ImportError:
    from models.configuration import Config

sys.modules['accuconf'] = sys.modules['accuconf_cfp']

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']
app.logger.info(app.url_map)

Bootstrap(app)
db = SQLAlchemy(app)

year = 2018

# app and db must be defined before these imports are executed as they are
# referred to by these modules. These modules will import accuconf.
from models.user import User
from models.security import MathPuzzle


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
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    edit_mode = False
    user = None
    if session.get("id", False):
        user = User.query.filter_by(email=session["id"]).first()
        if user is not None:
            edit_mode = True
    if request.method == "POST":
        email = request.form["email"]
        # In case that no user passphrase was provided, we don't update the field
        passphrase = None
        if len(request.form["passphrase"].strip()) > 0:
            passphrase = request.form["passphrase"]
        # TODO Should cpassphrase be handled like password and failure happen if they are not the same?
        cpassphrase = request.form["cpassphrase"]
        name = request.form["name"]
        town_and_city = request.form["towncity"]
        country = request.form["country"]
        state = request.form["state"]
        phone = request.form["phone"]
        postal_code = request.form["postalcode"]
        town_city = request.form['towncity']
        street_address = request.form['streetaddress']
        encoded_passphrase = None
        if type(passphrase) == str and len(passphrase):
            encoded_passphrase = hashlib.sha256(passphrase.encode('utf-8')).hexdigest()
        page = {}
        if edit_mode:
            user.email = email
            user.name = name
            if encoded_passphrase:
                user.passphrase = encoded_passphrase
            user.phone = phone
            user.country = country
            user.state = state
            user.postal_code = postal_code
            user.town_city = town_city
            user.street_address = street_address
            if encoded_passphrase:
                User.query.filter_by(email=user.email).update({'passphrase': encoded_passphrase })
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
            page["title"] = "Account update successful"
            page["data"] = "Your account details were successful updated."
        else:
            if not validate_email(email):
                page["title"] = "Registration failed"
                page["data"] = """Registration failed: Invalid/Duplicate user email.
Please register again"""
                return render_template("registration_failure.html", page=page)
            errors = []
            for field, field_name in (
                    (email, 'email'),
                    (passphrase, 'passphrase'),
                    (cpassphrase, 'passphrase confirmation'),
                    (name, 'name'),
                    (town_and_city, 'town and city'),
                    (phone, 'phone number'),
                    (postal_code, 'postal code'),
                    (street_address, 'street address'),):
                if not field.strip():
                    errors.append("The {} field was not filled in.".format(field_name))
            if errors:
                errors.append('')
                errors.append("Please register again")
                page = {
                    "title": "Registration failed",
                    "data": ' '.join(errors),
                }
                return render_template("registration_failure.html", page=page)
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
            page["title"] = "Registration successful"
            page["data"] = """You have successfully registered for submitting 
proposals for the ACCU Conf. Please login and
start preparing your proposal for the conference."""
        db.session.commit()
        return render_template("registration_success.html", page=page)
    elif request.method == "GET":
        num_a = randint(10, 99)
        num_b = randint(10, 99)
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


@app.route('/login')
def login():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    page = {'year': year}
    return render_template('login.html', page=page)


# /navlinks for the dynamic left-side menu

# /current_user ????
