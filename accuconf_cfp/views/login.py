from flask import redirect, render_template, request, session

from accuconf_cfp import app, year
from accuconf_cfp.utils import hash_passphrase, is_acceptable_route, is_valid_email, md

from models.user import User


def validate_login_data(login_data):
    if not login_data:
        return False, 'No JSON data returned.'
    mandatory_keys = ['email', 'passphrase']
    missing_keys = [key for key in mandatory_keys if key not in login_data]
    if missing_keys:
        return False, 'Missing keys in registration data: {}'.format(missing_keys)
    if not is_valid_email(login_data['email']):
        return False, 'The email address is invalid.'
    user = User.query.filter_by(email=login_data['email']).first()
    if not user or user.passphrase != hash_passphrase(login_data['passphrase']):
        return False, 'User/passphrase not recognised.'
    return user, None


@app.route('/login', methods=['GET', 'POST'])
def login():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    # TODO What to do if the user is currently logged in?
    page = {
        'title': 'Login',
        'year': year,
    }
    if request.method == 'POST':
        login_data = request.json
        user, message = validate_login_data(login_data)
        if not user:
            return render_template('general.html', page=md(page, {'data': message}))
        session['email'] = user.email
        #  TODO  Change something so as to see the login state. Menu changes of course.
        return render_template('general.html', page=md(page, {'data': 'Login successful.'}))
    else:
        return render_template('login.html', page=page)


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/')
