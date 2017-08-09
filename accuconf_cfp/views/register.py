from flask import jsonify, render_template, request, session

from accuconf_cfp import app, countries, db, year

import  accuconf_cfp.utils as utils

from models.user import User

# TODO find out why this has to be here.
from models.score import Score


def validate_registration_data(registration_data):
    """Check that all the submitted registration data is correct.

    A validation has happened client-side, so this is just repeating checks
    that are already known to have passed, there is no way this should ever
    fail,

    Passphrases are not checked here as they are mandatory for new registrations
    but not for registration edits.
    """
    if not registration_data:
        return False, 'No JSON data returned.'
    mandatory_keys = ['email', 'name', 'street_address', 'town_city', 'state', 'postal_code', 'country', 'phone']
    missing_keys = [key for key in mandatory_keys if key not in registration_data]
    if missing_keys:
        return False, 'Missing keys in registration data: {}'.format(missing_keys)
    validation_results = [getattr(utils, 'is_valid_' + key)(registration_data[key]) for key in mandatory_keys]
    validation_fails = [key for key, value in zip(mandatory_keys, validation_results) if not value]
    if validation_fails:
        return False, 'Validation failed for the following keys: {}.'.format(validation_fails)
    return True, None


base_page = {
    'year': year,
}


@app.route('/register', methods=['GET', 'POST'])
def register():
    check = utils.is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    assert 'email' not in session
    if request.method == 'POST':
        registration_data = request.json
        status, message = validate_registration_data(registration_data)
        if not status:
            # NB This should never be executed.
            response = jsonify(message)
            response.status_code = 400
            return response
        if not registration_data['passphrase']:
            # NB This should never be executed.
            response = jsonify('No passphrase for new registration.')
            response.status_code = 400
            return response
        if User.query.filter_by(email=registration_data['email']).first():
            # Currently this can happen as client-site checking is not implemented.
            # TODO implement client side checking so this becomes redundant.
            response = jsonify('The email address is already in use.')
            response.status_code = 400
            return response
        registration_data['passphrase'] = utils.hash_passphrase(registration_data['passphrase'])
        db.session.add(User(**registration_data))
        db.session.commit()
        return jsonify('register_success')
    return render_template('register.html', page=utils.md(base_page, {
            'title': 'Register',
            'data': 'Register here for submitting proposals to the ACCU {} Conference'.format(year),
            'submit_button': 'Register',
            'countries': sorted(list(countries.keys())),
        }))


@app.route('/register_success')
def register_success():
    check = utils.is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    return render_template("general.html", page=utils.md(base_page, {
        'title': 'Registration Successful',
        'data': '''
You have successfully registered for submitting proposals for the ACCU Conf.

Please login and start preparing your proposal for the conference.
'''}))


@app.route('/registration_update', methods=['GET', 'POST'])
def registration_update():
    check = utils.is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    if not utils.is_logged_in():
        return render_template('general.html', page=utils.md(base_page, {
            'title': 'Registration Update Failure',
            'data': 'You must be logged in to update registration details.',
        }))
    user = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        registration_data = request.json
        status, message = validate_registration_data(registration_data)
        if not status:
            # NB This should never be executed.
            response = jsonify(message)
            response.status_code = 400
            return response
        if registration_data['passphrase']:
            registration_data['passphrase'] = utils.hash_passphrase(registration_data['passphrase'])
        User.query.filter_by(email=registration_data['email']).update(registration_data)
        db.session.commit()
        return jsonify('registration_update_success')
    return render_template('register.html', page=utils.md(base_page, {
        'title': 'Registration Details Updating',
        'email': user.email,
        'name': user.name,
        'phone': user.phone,
        'street_address': user.street_address,
        'town_city': user.town_city,
        'state': user.state,
        'postal_code': user.postal_code,
        'country': user.country,
        'data': 'Here you can edit your registration information',
        'submit_button': 'Save',
        'countries': sorted(list(countries.keys())),
    }))


@app.route('/registration_update_success')
def registration_update_success():
    check = utils.is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    if not utils.is_logged_in():
        return render_template('general.html', page=utils.md(base_page, {
            'title': 'Registration Update Failure',
            'data': 'You must be logged in to update registration details.',
        }))
    return render_template('general.html',  page=utils.md(registration_update_base_page, {
        'title': 'Registration Update Successful',
        'data': '''
Your registration details were successful updated.
'''}))
