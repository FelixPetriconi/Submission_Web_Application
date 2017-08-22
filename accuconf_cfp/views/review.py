from flask import render_template, session

from accuconf_cfp import app, year
from accuconf_cfp.utils import is_acceptable_route, is_logged_in, md

from models.user import User
from models.role_types import Role

base_page = {
    'year': year,
}


@app.route('/review_list')
def review_list():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    if is_logged_in():
        user = User.query.filter_by(email=session['email']).first()
        if not user:
            render_template('/general.html', page=md(base_page, {
                'pagetitle': 'Review List Failed',
                'data': 'Logged in user is not a registered user. This cannot happen.',
            }))
        if user.role != Role.reviewer:
            render_template('/general.html', page=md(base_page, {
                'pagetitle': 'Review List Failed',
                'data': 'Logged in user is not a registered reviewer.',
            }))
        render_template('/review_list.html', page=md(base_page, {
            'pagetitle': 'List of Proposals',
            'data': 'Please click on the proposal you wish to review.',
        }))
    return render_template('review_list.html', page=md(base_page, {
        'pagetitle': 'Review List Failed',
        'data': 'You must be registered, logged in, and a reviewer to review proposals',
    }))


@app.route('/review_proposal/<int:id>')
def review_proposal(id):
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    return render_template('review_proposal.html', page=md(base_page, {
        'pagetitle': 'Review Proposal Failed',
        'data': 'You must be registered, logged in, and a reviewer to review a proposal',
    }))
