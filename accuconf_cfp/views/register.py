import random

from flask import render_template, request, session

from accuconf_cfp import app, countries, db, year

from accuconf_cfp.utils import hash_passphrase, is_acceptable_route, is_logged_in, is_valid_email, md

from models.user import User


def validate_registration_data(registration_data):
    """Check that all the submitted registration data is correct.

    A validation has happened client-side, so this is just repeating checks
    that are already known to have passed, there is no way this should ever
    fail,
    """
    if not registration_data:
        return False, 'No JSON data returned.'
    mandatory_keys = ['email', 'name', 'passphrase', 'country', 'state', 'postal_code', 'street_address', 'phone']
    missing_keys = [key for key in mandatory_keys if key not in registration_data]
    if missing_keys:
        return False, 'Missing keys in registration data: {}'.format(missing_keys)
    if not is_valid_email(registration_data['email']):
        return False, 'The email address is invalid.'
    return True, None


@app.route('/register', methods=['GET', 'POST'])
def register():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    user = User.query.filter_by(email=session['email']).first() if is_logged_in() else None
    edit_mode = bool(user)
    page = {
        'type': 'Registration',
        'year': year,
    }
    if request.method == 'POST':
        registration_data = request.json
        status, message = validate_registration_data(registration_data)
        if not status:
            # NB This should never be executed.
            return render_template('failure.html', page=md(page, {'data': message}))
        if not edit_mode:
            if not registration_data['passphrase']:
                return render_template('failure.html', page=md(page, {'data': 'No passphrase for new registration.'}))
            if User.query.filter_by(email=registration_data['email']).first():
                return render_template('failure.html', page=md(page, {'data': 'The email address is already in use.'}))
        if edit_mode:
            User.query.filter_by(email=registration_data['email']).update(registration_data)
            db.session.commit()
            return render_template('success.html', page=md(page, {'data': 'Your account details were successful updated.'}))
        db.session.add(User(**registration_data))
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
            'countries': sorted(list(countries.keys())),
        }))
