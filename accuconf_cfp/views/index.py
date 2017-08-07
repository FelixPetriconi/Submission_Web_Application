from flask import render_template

from accuconf_cfp import app, year


@app.route('/')
def index():
    page = {
        'title': 'Call for Proposals',
        'year': year,
    }
    if app.config['MAINTENANCE']:
        return render_template('maintenance.html', page=page)
    if not (app.config['CALL_OPEN'] or app.config['REVIEWING_ALLOWED']):
        return render_template('not_open.html', page=page)
    return render_template('open_home.html', page=page)
