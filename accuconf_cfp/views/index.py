from flask import render_template

from accuconf_cfp import app, year

from accuconf_cfp.utils import md


@app.route('/')
def index():
    page = {
        'title': 'Call for Proposals',
        'year': year,
    }
    if app.config['MAINTENANCE']:
        return render_template('general.html', page=md(page, {'data': '''
The ACCU {{page.year }} proposal submission Web application is currently undergoing maintenance.
This should not take long, so please come back soon.
'''}))
    if app.config['CALL_OPEN']:
        return render_template('general.html', page=md(page, {'data': '''
The ACCU {{ page.year }} Call for Proposals is open for business.
'''}))
    return render_template('general.html', page=md(page, {'data': '''
The ACCU {{ page.year }} Call for Proposals is not open.
'''}))
