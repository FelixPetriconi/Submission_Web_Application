from flask import render_template

from accuconf_cfp import app, year

from accuconf_cfp.utils import md


@app.route('/')
def index():
    page = {
        'pagetitle': 'Call for Proposals',
        'year': year,
    }
    if app.config['MAINTENANCE']:
        return render_template('general.html', page=md(page, {'data': '''
The ACCU {} proposal submission Web application is currently undergoing maintenance.
This should not take long, so please come back soon.
'''.format(year)}))
    if app.config['CALL_OPEN']:
        return render_template('general.html', page=md(page, {'data': '''
The ACCU {} Call for Proposals is open for business.
'''.format(year)}))
    return render_template('general.html', page=md(page, {'data': '''
The ACCU {} Call for Proposals is not open.
'''.format(year)}))
