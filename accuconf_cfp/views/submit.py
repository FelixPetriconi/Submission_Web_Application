from flask import jsonify, render_template, request, session

from accuconf_cfp import app, db, year, countries
from accuconf_cfp.utils import is_acceptable_route, is_logged_in, md

from models.user import User
from models.proposal import Presenter, Proposal, ProposalPresenter
from models.proposal_types import SessionType

base_page = {
    'year': year,
}


def validate_presenters(presenters):
    """Check validity of  the list of presenters.

    This function should never fail since the checks should already have been made client-side.
     """
    mandatory_keys = ["lead", "email", "name", "bio", "country", "state"]
    lead_found = False
    lead_presenter = ""
    for presenter in presenters:
        for key in mandatory_keys:
            if key not in presenter:
                return False, "{} attribute is mandatory for Presenters".format(key)
            if presenter[key] is None:
                return False, "{} attribute should have valid data".format(key)
        if "lead" in presenter and "email" in presenter:
            if presenter["lead"] and lead_found:
                return False, "{} and {} are both marked as lead presenters".format(presenter["email"], lead_presenter)
            elif presenter["lead"] and not lead_found:
                lead_found = True
                lead_presenter = presenter["email"]
    return True, "validated"


def validate_proposal_data(proposal_data):
    """Check validity of the proposal data.

    This function should never fail since the checks should already have been made client-side.
    """
    mandatory_keys = ['title', 'summary', 'session_type', 'presenters']
    for key in mandatory_keys:
        if key not in proposal_data:
            return False, '{} information is not present in proposal'.format(key)
        if proposal_data[key] is None:
            return False, '{} information should not be empty'.format(key)
    if len(proposal_data.get('title')) < 5:
        return False, 'Title is too short'
    if len(proposal_data.get('summary')) < 50:
        return False, 'Summary is too short'
    if type(proposal_data['presenters']) != list:
        return False, 'Presenters data is malformed'
    if len(proposal_data['presenters']) < 1:
        return False, 'At least one presenter needed'
    (result, message) = validate_presenters(proposal_data['presenters'])
    if not result:
        return result, message
    return True, 'validated'


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    if is_logged_in():
        if request.method == 'POST':
            user = User.query.filter_by(email=session['email']).first()
            if user:
                proposal_data = request.json
                print(proposal_data)
                status, message = validate_proposal_data(proposal_data)
                if not status:
                    # NB This should never be executed.
                    response = jsonify(message)
                    response.status_code = 400
                    return response
                proposal = Proposal(
                    user,
                    proposal_data.get('title').strip(),
                    SessionType(proposal_data.get('session_type').strip()),
                    proposal_data.get('summary').strip()
                )
                db.session.add(proposal)
                presenters_data = proposal_data.get('presenters')
                for presenter_data in presenters_data:
                    presenter = Presenter(
                        presenter_data['email'],
                        presenter_data['name'],
                        presenter_data['bio'],
                        presenter_data['country'],
                        presenter_data['state'],
                    )
                    ProposalPresenter(proposal, presenter, presenter_data['lead'])
                    db.session.add(presenter)
                db.session.commit()
                session['just_submitted'] = True
                return jsonify('submit_success')
            return render_template('general.html', page=md(base_page, {
                'title': 'Submit POST Error',
                'data': 'The logged in user is not in database. This cannot happen.',
            }))
        user = User.query.filter_by(email=session['email']).first()
        if user:
            return render_template('submit.html', page=md(base_page, {
                'title': 'Submit a proposal for ACCU {}'.format(year),
                'name': user.name,
                'proposer': {
                    'email': user.email,
                    'name': user.name,
                    'bio': 'A human being we know, but we need something somewhat more uniquely personal.',
                    'country': user.country,
                    'state': user.state,
                },
                'countries': sorted(countries.keys())
            }))
        return render_template('general.html', page=md(base_page, {
            'title': 'Submission Problem',
            'data': 'The logged in user is not in database. This cannot happen.',
        }))
    return render_template('general.html', page=md(base_page, {
        'title': 'Submit Not Possible',
        'data': 'You must be registered and logged in to submit a proposal.'
    }))


@app.route('/submit_success')
def submit_success():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    if 'just_submitted' in session:
        session.pop('just_submitted', None)
        return render_template('general.html', page=md(base_page, {
            'title': 'Submission Successful',
            'data': '''
Thank you, you have successfully submitted a proposal for the ACCU {} conference!
If you need to edit it you can via the 'My Proposal' menu item.
'''.format(year),
        }))
    return render_template('general.html', page=md(base_page, {
        'title': 'Submit Failed',
        'data': 'You must be registered and logged in to submit a proposal.',
    }))


@app.route('/my_proposals')
def my_proposals():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    if is_logged_in():
        user = User.query.filter_by(email=session['email']).first()
        return render_template('my_proposals.html', page=md(base_page, {
            'title': 'My Proposals',
            'data': '''
The following are your current proposals. Click on the one you wish to update.
''',
            'proposals': [{'title': proposal.title, 'id': proposal.id} for proposal in user.proposals]
        }))
    return render_template('general.html', page=md(base_page, {
        'title': 'My Proposals Failure',
        'year': year,
        'data': 'You must be registered and logged in to discover your current proposals.',
    }))


@app.route('/proposal_update/<int:id>')
def proposal_update(id):
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    if is_logged_in():
        proposal = Proposal.query.filter_by(id=id).first()
        if not proposal:
            return render_template('general.html', page=md(page, {
                'title': 'Proposal Not Found',
                'data': 'The requested proposal cannot be found.'
            }))
        return render_template('submit.html', page=md(base_page, {
            'title': 'Update a proposal for ACCU {}'.format(year),
            'name': proposal.proposer.name,
            'proposer': {
                'email': proposal.proposer.email,
                'name': proposal.proposer.name,
                'country': proposal.proposer.country,
                'state': proposal.proposer.state,
            },
            'countries': sorted(countries.keys())
        }))
    return render_template('general.html', page=md(base_page, {
        'title': 'Proposal Update Failure',
        'data': 'You must be registered and logged in to update a proposal.',
    }))
