from flask import jsonify, render_template, request, session

from accuconf_cfp import app, db, year
from accuconf_cfp.utils import is_acceptable_route, is_logged_in, md, validate_proposal_data

from models.user import User
from models.proposal import Presenter, Proposal, ProposalPresenter
from models.proposal_types import SessionType


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    page = {
        'title': 'Submit',
        'year': year,
    }
    if is_logged_in():
        if request.method == 'POST':
            user = User.query.filter_by(email=session['email']).first()
            if user:
                proposal_data = request.json
                status, message = validate_proposal_data(proposal_data)
                response = {}
                if status:
                    proposal = Proposal(
                        user,
                        proposal_data.get('title').strip(),
                        SessionType(proposal_data.get('session_type')),
                        proposal_data.get('abstract').strip()
                    )
                    db.session.add(proposal)
                    presenters_data = proposal_data.get('presenters')
                    for presenter_data in presenters_data:
                        presenter = Presenter(
                            presenter_data['email'],
                            presenter_data['name'],
                            'A human being.',
                            presenter_data['country'],
                            presenter_data['state'],
                        )
                        ProposalPresenter(proposal, presenter, presenter_data['lead'])
                        db.session.add(presenter)
                    db.session.commit()
                    response['success'] = True
                    response['message'] = '''Thank you, you have successfully submitted a proposal for the ACCU {} conference!
If you need to edit it you can via the 'My Proposal' menu item.'''.format(year)
                    response['redirect'] = '/'
                else:
                    response['success'] = False
                    response['message'] = message
                return jsonify(**response)
        else:
            user = User.query.filter_by(email=session['email']).first()
            if user:
                return render_template('submit.html', page={
                    'title': 'Submit a proposal for ACCU {}'.format(year),
                    'name': user.name,
                    'proposer': {
                        'email': user.email,
                        'name': user.name,
                        'bio': 'A human being.',
                        'country': user.country,
                        'state': user.state,
                    }
                })
    return render_template('failure.html', page=md(page, {'data': 'Must be logged in to submit a proposal.'}))
