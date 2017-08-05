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
    'type': 'Registration',
    'year': year,
}


@app.route('/register', methods=['GET', 'POST'])
def register():
    check = utils.is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    user = User.query.filter_by(email=session['email']).first() if utils.is_logged_in() else None
    edit_mode = bool(user)
    if request.method == 'POST':
        registration_data = request.json
        status, message = validate_registration_data(registration_data)
        if not status:
            # NB This should never be executed.
            response = jsonify(message)
            response.status_code = 400
            return response
        if not edit_mode:
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
        if registration_data['passphrase']:
            registration_data['passphrase'] = utils.hash_passphrase(registration_data['passphrase'])
        if edit_mode:
            User.query.filter_by(email=registration_data['email']).update(registration_data)
            db.session.commit()
            return jsonify('register_success_update')
        db.session.add(User(**registration_data))
        db.session.commit()
        return jsonify('register_success_new')
    else:
        return render_template('register.html', page=utils.md(base_page, {
            'email': user.email if edit_mode else '',
            'name': user.name if edit_mode else '',
            'phone': user.phone if edit_mode else '',
            'street_address': user.street_address if edit_mode else '',
            'town_city': user.town_city if edit_mode else '',
            'state': user.state if edit_mode else '',
            'postal_code': user.postal_code if edit_mode else '',
            'country': user.country if edit_mode else 'GBR',  # UK shall be the default
            'title': 'Account Information' if edit_mode else 'Register',
            'data': 'Here you can edit your account information' if edit_mode else 'Register here for submitting proposals to ACCU Conference',
            'submit_button': 'Save' if edit_mode else 'Register',
            'countries': sorted(list(countries.keys())),
        }))


@app.route('/register_success_new')
def register_success_new():
    return render_template("success.html", page=utils.md(base_page, {'data': '''
You have successfully registered for submitting proposals for the ACCU Conf.

Please login and start preparing your proposal for the conference.
'''}))


@app.route('/register_success_update')
def register_success_update():
    return render_template('success.html',  page=utils.md(base_page, {'data': '''
Your account details were successful updated.
'''}))