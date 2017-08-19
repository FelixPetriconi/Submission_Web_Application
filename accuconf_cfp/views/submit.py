from flask import jsonify, render_template, request, session

from accuconf_cfp import app, db, year, countries
from accuconf_cfp.utils import (is_acceptable_route, is_logged_in, md,
                                is_valid_email, is_valid_country, is_valid_name,
                                is_valid_bio, is_valid_passphrase,
                                is_valid_phone, is_valid_postal_code, is_valid_state,
                                is_valid_street_address, is_valid_town_city
                                )

from models.user import User
from models.proposal import Presenter, Proposal, ProposalPresenter
from models.proposal_types import SessionAudience, SessionType

base_page = {
    'year': year,
}


def validate_presenters(presenters):
    """Check validity of  the list of presenters.

    This function should never fail since the checks should already have been made client-side.
     """
    mandatory_keys = ['is_lead', 'email', 'name', 'bio', 'country', 'state']
    leads_found = []
    for presenter in presenters:
        for key in mandatory_keys:
            if key not in presenter:
                return False, '{} attribute is mandatory for Presenters'.format(key)
            if presenter[key] is None:
                return False, '{} attribute should have valid data'.format(key)
        if not is_valid_email(presenter['email']):
            return False, '{} not a valid email'.format(presenter['email'])
        if not is_valid_name(presenter['name']):
            return False, '{} not a valid name'.format(presenter['name'])
        if not is_valid_bio(presenter['bio']):
            return False, '{} not a valid bio'.format(presenter['bio'])
        if not is_valid_state(presenter['state']):
            return False, '{} not a valid state'.format(presenter['state'])
        if not is_valid_country(presenter['country']):
            return False, '{} not a valid country'.format(presenter['country'])
        if presenter['is_lead']:
            leads_found.append(presenter['email'])
    lead_count = len(leads_found)
    if lead_count == 0:
        return False, 'No lead presenter.'
    elif lead_count > 1:
        return False, '{} marked as lead presenters'.format(leads_found)
    return True, 'validated'


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
    if len(proposal_data.get('title')) < 8:
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
                status, message = validate_proposal_data(proposal_data)

                print('XXXX', proposal_data)
                print('XXXX', status, '-', message)

                if not status:
                    # NB This should never be executed.
                    response = jsonify(message)
                    response.status_code = 400
                    return response
                proposal = Proposal(
                    user,
                    proposal_data.get('title').strip(),
                    SessionType(proposal_data.get('session_type').strip()),
                    proposal_data.get('summary').strip(),
                    proposal_data.get('notes').strip() if proposal_data.get('notes') else '',
                    proposal_data.get('constraints').strip() if proposal_data.get('constraints') else '',
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
                    ProposalPresenter(proposal, presenter, presenter_data['is_lead'])
                    db.session.add(presenter)
                db.session.commit()
                session['just_submitted'] = True
                return jsonify('submit_success')
            return render_template('general.html', page=md(base_page, {
                'pagetitle': 'Submit POST Error',
                'data': 'The logged in user is not in database. This cannot happen.',
            }))
        user = User.query.filter_by(email=session['email']).first()
        if user:
            return render_template('submit.html', page=md(base_page, {
                'pagetitle': 'Submit a proposal',
                'title': '',
                'session_type': SessionType.session.value,
                'summary': '',
                'audience': SessionAudience.all.value,
                'category': '',
                'notes': '',
                'constraints': '',
                'presenter': {
                    'email': user.email,
                    'name': user.name,
                    'is_lead': True,
                    'bio': '',
                    'country': user.country,
                    'state': user.state,
                },
                'countries': sorted(countries.keys())
            }))
        return render_template('general.html', page=md(base_page, {
            'pagetitle': 'Submission Problem',
            'data': 'The logged in user is not in database. This cannot happen.',
        }))
    return render_template('general.html', page=md(base_page, {
        'pagetitle': 'Submit Not Possible',
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
            'pagetitle': 'Submission Successful',
            'data': '''
Thank you, you have successfully submitted a proposal for the ACCU {} conference!
If you need to edit it you can via the 'My Proposal' menu item.
'''.format(year),
        }))
    return render_template('general.html', page=md(base_page, {
        'pagetitle': 'Submit Failed',
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
            'pagetitle': 'My Proposals',
            'data': 'The following are your current proposals. Click on the one you wish to update.',
            'proposals': [{'title': proposal.title, 'id': proposal.id} for proposal in user.proposals]
        }))
    return render_template('general.html', page=md(base_page, {
        'pagetitle': 'My Proposals Failure',
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
        proposal_presenter = ProposalPresenter.query.filter_by(proposal=proposal).first()
        if not proposal:
            return render_template('general.html', page=md(base_page, {
                'pagetitle': 'Proposal Not Found',
                'data': 'The requested proposal cannot be found.'
            }))
        # TODO How to deal with multi-presenter proposals?
        presenter = proposal.presenters[0]
        return render_template('submit.html', page=md(base_page, {
            'pagetitle': 'Update a proposal for ACCU {}'.format(year),
            'title': proposal.title,
            'session_type': proposal.session_type,
            'summary': proposal.summary,
            'audience': proposal.audience,
            'category': proposal.category,
            'notes': proposal.notes,
            'constraints': proposal.constraints,
            'presenter': {
                'email': presenter.email,
                'name': presenter.name,
                'is_lead': proposal_presenter.is_lead,
                'bio': presenter.bio,
                'country': presenter.country,
                'state': presenter.state,
            },
            'countries': sorted(countries.keys())
        }))
    return render_template('general.html', page=md(base_page, {
        'pagetitle': 'Proposal Update Failure',
        'data': 'You must be registered and logged in to update a proposal.',
    }))
