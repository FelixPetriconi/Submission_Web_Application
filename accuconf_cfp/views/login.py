"""The routes associated with logging in and out."""

from flask import jsonify, redirect, render_template, request, session, Markup

from accuconf_cfp import app, year
from accuconf_cfp.utils import hash_passphrase, is_acceptable_route, is_logged_in, is_valid_email, md

from models.user import User

base_page = {
    'year': year,
}


def validate_login_data(login_data):
    """Check some aspects of putative login details.

    Return a pair with the zero element being a Boolean determining whether validation
    has been successful, the one element is a message in the case of failure and "validated"
    in the case of success.
    """
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
    check = is_acceptable_route(True)
    if not check[0]:
        return check[1]
    assert check[1] is None
    if  is_logged_in():
        return redirect('/')
    # TODO What to do if the user is currently logged in?
    if request.method == 'POST':
        login_data = request.json
        user, message = validate_login_data(login_data)
        if not user:
            # This should never happen.
            response = jsonify(message)
            response.status_code = 400
            return response
        session['email'] = user.email
        session['just_logged_in'] = True
        #  TODO  Change something so as to see the login state. Menu changes of course.
        return jsonify('login_success')
    return render_template('login.html', page=md(base_page, {
            'pagetitle': 'Login',
            'data': 'Please login using email and passphrase given at registration time.',
        }))


@app.route('/login_success')
def login_success():
    check = is_acceptable_route(True)
    if not check[0]:
        return check[1]
    assert check[1] is None
    if 'just_logged_in' not in session:
        return redirect('/')
    session.pop('just_logged_in', None)
    if is_logged_in():
        return render_template('general.html', page=md(base_page, {
            'pagetitle': 'Login Successful',
            'data': Markup('''
Login successful.
</p>
<p>
The menu on the left should now show entries for submitting a new proposal,
amending the registration details for the logged in user, listing the previously
submitted proposals, or logging out.
</p>
<p>
if you have not previously submitted a proposal the "My Proposals" list will be empty.
Once you have submitted one or more proposals, they can be amended via the
"My Proposals" list.
'''),
        }))
    return render_template('login.html', page=md(base_page, {
        'pagetitle': 'Login Failure',
        'data': 'Please login using email and passphrase given at registration time.',
    }))


@app.route('/logout')
def logout():
    check = is_acceptable_route(True)
    if not check[0]:
        return check[1]
    assert check[1] is None
    session.pop('email', None)
    return redirect('/')
