import pathlib
import sys

from flask import jsonify, request

from server_configuration import host, port

sys.path.insert(0, str(pathlib.PurePath(__file__).parent.parent))

from accuconf_cfp import app, db
import accuconf_cfp.utils as utils
from accuconf_cfp.views.register import validate_registration_data

from models.user import User
from models.role_types import Role

app.config['CALL_OPEN'] = True
app.config['REVIEWING_ALLOWED'] = True
app.config['MAINTENANCE'] = False
app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'


@app.route('/register_reviewer', methods=['POST'])
def register_reviewer():
    registration_data = request.json
    status, message = validate_registration_data(registration_data)
    if not status:
        raise ValueError(message)
    if not registration_data['passphrase']:
        raise ValueError('No passphrase for new registration.')
    if User.query.filter_by(email=registration_data['email']).first():
        raise ValueError('The email address is already in use.')
    registration_data['passphrase'] = utils.hash_passphrase(registration_data['passphrase'])
    registration_data['role'] = Role.reviewer
    db.session.add(User(**registration_data))
    db.session.commit()
    return jsonify('Reviewer added.')


db.drop_all()
db.create_all()

app.run(host=host, port=port, debug=False)
