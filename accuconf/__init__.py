from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

try:
    from accuconf_config import Config
except ImportError:
    from .configuration import Config

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']
app.logger.info(app.url_map)

Bootstrap(app)
db = SQLAlchemy(app)


@app.route('/')
def index():
    if app.config['MAINTENANCE']:
        return 'Maintenance of ACCU website'
    if not (app.config['CALL_OPEN'] or app.config['REVIEWING_ALLOWED']):
        return 'ACCU Submission Web application not available.'
    return 'Hello from ACCU. Register or Login'


@app.route('/register')
def register():
    if app.config['MAINTENANCE']:
        return 'Maintenance of ACCU website'
    if not (app.config['CALL_OPEN'] or app.config['REVIEWING_ALLOWED']):
        return 'ACCU Submission Web application not available.'
    return 'Hello from ACCU. Register'


@app.route('/login')
def login():
    if app.config['MAINTENANCE']:
        return 'Maintenance of ACCU website'
    if not (app.config['CALL_OPEN'] or app.config['REVIEWING_ALLOWED']):
        return 'ACCU Submission Web application not available.'
    return 'Hello from ACCU. Login'


