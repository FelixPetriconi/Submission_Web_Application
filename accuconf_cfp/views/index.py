"""The top level, / or /index.html."""

from flask import render_template, Markup

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
        return render_template('general.html', page=md(page, {'data': Markup('''
The ACCU {} Call for Proposals is open for business.
</p>
<i>
<p>
This Web application is just for submitting proposals, the
<a href="https://conference.accu.org">main website</a>
 is where to go to get information about the conference. 
</p>
<p>
There are two blog posts that might be particularly interesting for submitters:
</p>
<ul>
<li>
<a href="https://conference.accu.org/posts/2017/201710150748_proposalsforaccu2018.html">Proposals for ACCU 2018</a>
</li>
<li>
<a href="https://conference.accu.org/posts/2017/201710150836_whatsaccuabout.html">What's ACCU About</a> 
</li>
</ul>
</i>
<p>
Using the menu items on the left, you can register, if you are not already registered,
or login if you are already registered – you have to have registered in order to login.
</p>
<p>
You will have to click one of them to do more than look at this screen. :-)
'''.format(year))}))
    return render_template('general.html', page=md(page, {'data': '''
The ACCU {} Call for Proposals is not open.
'''.format(year)}))
