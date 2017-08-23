"""Routes associated with reviewing submitted proposals."""

from flask import render_template, session

from accuconf_cfp import app, year
from accuconf_cfp.utils import is_acceptable_route, is_logged_in, md

from models.user import User
from models.proposal import Proposal
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
            return render_template('/general.html', page=md(base_page, {
                'pagetitle': 'Review List Failed',
                'data': 'Logged in user is not a registered user. This cannot happen.',
            }))
        if user.role != Role.reviewer:
            return render_template('/general.html', page=md(base_page, {
                'pagetitle': 'Review List Failed',
                'data': 'Logged in user is not a registered reviewer.',
            }))
        proposals = [(p.id, p.title, lead.presenter.name)
                     for p in Proposal.query.all() if p.proposer != user
                     for lead in p.proposal_presenters if lead.is_lead
                     ]
        return render_template('/review_list.html', page=md(base_page, {
            'pagetitle': 'List of Proposals',
            'data': 'Please click on the proposal you wish to review.',
            'proposals': proposals,
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
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    if is_logged_in():
        user = User.query.filter_by(email=session['email']).first()
        if not user:
            return render_template('/general.html', page=md(base_page, {
                'pagetitle': 'Review Proposal Failed',
                'data': 'Logged in user is not a registered user. This cannot happen.',
            }))
        if user.role != Role.reviewer:
            return render_template('/general.html', page=md(base_page, {
                'pagetitle': 'Review Proposal Failed',
                'data': 'Logged in user is not a registered reviewer.',
            }))
        proposal = Proposal.query.filter_by(id=id).first()
        presenters = [{'name': p.name, 'bio': p.bio} for p in proposal.presenters]
        return render_template('/review_proposal.html', page=md(base_page, {
            'pagetitle': 'Proposals to Review',
            'data': 'There is no specific "do nothing" button, to not do anything simply navigate away from this page.',
            'title': proposal.title,
            'summary': proposal.summary,
            'notes': proposal.notes,
            'presenters': presenters,
            'button_label': 'Submit',
        }))
    return render_template('review_proposal.html', page=md(base_page, {
        'pagetitle': 'Review Proposal Failed',
        'data': 'You must be registered, logged in, and a reviewer to review a proposal',
    }))
