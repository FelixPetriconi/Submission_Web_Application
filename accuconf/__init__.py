from flask import Flask, render_template
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


def is_acceptable_route():
    """Check the state of the application and return a pair.

    The first item of the pair is a Boolean stating whether the route is acceptable.
    The second item of the pair is a rendered template to display if the route is not
     allowed, and None if it is.
    """
    if app.config['MAINTENANCE']:
        return (False, render_template('maintenance.html'))
    if not app.config['CALL_OPEN']:
        if app.config['REVIEWING_ALLOWED']:
            return (True, None)
        return (False, render_template('not_open.html'))
    return (True, None)


@app.route('/')
def index():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    return 'Hello from ACCU. Register or Login'


@app.route('/register')
def register():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    return 'Hello from ACCU. Register'


@app.route('/login')
def login():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    return 'Hello from ACCU. Login'


# /navlinks for the dynamic left-side menu

# /current_user ????