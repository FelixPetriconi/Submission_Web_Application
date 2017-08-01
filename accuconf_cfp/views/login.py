import hashlib

from flask import redirect, render_template, request, session

from accuconf_cfp import app, year
from accuconf_cfp.utils import is_acceptable_route

from accuconf_cfp.utils import md

from models.user import User


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
