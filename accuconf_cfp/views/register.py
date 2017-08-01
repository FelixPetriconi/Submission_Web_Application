import hashlib
import random

from flask import render_template, request, session

from accuconf_cfp import app, countries, db, year

from accuconf_cfp.utils import is_acceptable_route, is_logged_in, md, is_valid_new_email

from models.user import User


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
