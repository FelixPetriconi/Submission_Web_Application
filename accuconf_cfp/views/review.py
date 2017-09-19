"""Routes associated with reviewing submitted proposals."""

from flask import jsonify, render_template, request, session

from accuconf_cfp import app, db, year
from accuconf_cfp.utils import is_acceptable_route, is_logged_in, md

from models.proposal import Proposal
from models.role_types import Role
from models.score import Comment, Score
from models.user import User

base_page = {
    'year': year,
}


def already_reviewed(proposal, reviewer):
    return any(x.proposal == proposal for x in reviewer.scores)


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
        # TODO reviewer can review proposed proposal (done) but what about being a presenter?
        proposals = [(p.id, p.title, lead.presenter.name, already_reviewed(p, user))
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


@app.route('/review_proposal/<int:id>', methods=['GET', 'POST'])
def review_proposal(id):
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    if is_logged_in():
        if request.method == 'POST':
            review_data = request.json
            reviewer = User.query.filter_by(email=session['email']).first()
            if not reviewer:
                response = jsonify('Logged in person is not a reviewer. This cannot happen.')
                response.status_code = 400
                return response
            proposal = Proposal.query.filter_by(id=id).first()
            if not proposal:
                response = jsonify('Proposal cannot be found. This cannot happen.')
                response.status_code = 400
                return response
            db.session.add(Score(proposal, reviewer, review_data['score']))
            if review_data['comment']:
                db.session.add(Comment(proposal, reviewer, review_data['comment']))
            db.session.commit()
            return jsonify('Review stored.')
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
        # TODO do not display if the reviewer is the proposer or one of the presenters.
        return render_template('/review_proposal.html', page=md(base_page, {
            'pagetitle': 'Proposal to Review',
            'data': 'There is no specific "do nothing" button, to not do anything simply navigate away from this page.',
            'proposal_id': id,
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
