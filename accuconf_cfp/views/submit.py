"""Routes associated with submitting and amending submitted proposals."""

from flask import jsonify, render_template, request, session, Markup

from accuconf_cfp import app, db, year, countries
from accuconf_cfp.utils import (is_acceptable_route, is_logged_in, md,
                                is_valid_email, is_valid_country, is_valid_name,
                                is_valid_bio, is_valid_passphrase,
                                is_valid_phone,
                                send_email_to,
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
    mandatory_keys = ['is_lead', 'email', 'name', 'bio', 'country']
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


submit_form_preface_markup = '''
The Summary and Bio entries can be plain text or AsciiDoc fragments (assumed UTF-8 encoded).
If you use AsciiDoc and want to use section heads then for the Summary start with the third level (====), and
for the Bio start with the second level (===). Level zero and one (and for session descriptions, two) section heads
are used in the website production system.
</p>
<p>
All other text entry fields are plain text (assumed UTF-8 encoded).
</p>
<p>
<em>All conference sessions, except workshops, will be videoed, and the video published on the ACCUConf YouTube channel,
except in the cases the "no video" box is ticked.</em>
'''


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
                if not status:
                    # NB This should never be executed.
                    response = jsonify(message)
                    response.status_code = 400
                    return response
                proposal = Proposal(
                    user,
                    proposal_data.get('title').strip(),
                    proposal_data.get('summary').strip(),
                    SessionType(proposal_data.get('session_type').strip()),
                    SessionAudience(proposal_data.get('audience').strip()) if proposal_data.get('audience') else SessionAudience.all,
                    proposal_data.get('keywords').strip() if proposal_data.get('keywords') else '',
                    proposal_data.get('no_video') if proposal_data.get('no_video') else False,
                    proposal_data.get('notes').strip() if proposal_data.get('notes') else '',
                    proposal_data.get('constraints').strip() if proposal_data.get('constraints') else '',
                )
                db.session.add(proposal)
                presenters_data = proposal_data.get('presenters')
                for presenter_data in presenters_data:
                    presenter = Presenter.query.filter_by(email=presenter_data['email']).all()
                    if presenter:
                        assert len(presenter) == 1
                        presenter = presenter[0]
                        if presenter.name != presenter_data['name']:
                            presenter.name = presenter_data['name']
                        if presenter.bio != presenter_data['bio']:
                            presenter.bio = presenter_data['bio']
                        if presenter.country != presenter_data['country']:
                            presenter.country = presenter_data['country']
                    else:
                        presenter = Presenter(
                            presenter_data['email'],
                            presenter_data['name'],
                            presenter_data['bio'],
                            presenter_data['country'],
                        )
                        db.session.add(presenter)
                    ProposalPresenter(proposal, presenter, presenter_data['is_lead'])
                db.session.commit()
                session['just_submitted'] = True
                return jsonify('submit_success')
            return render_template('general.html', page=md(base_page, {
                'pagetitle': 'Submit POST Error',
                'data': 'The logged in user is not in database. This cannot happen.',
            }))
        user = User.query.filter_by(email=session['email']).first()
        if user:
            presenter = Presenter.query.filter_by(email=user.email).all()
            if presenter:
                assert len(presenter) == 1
                presenter = presenter[0]
                (p_email, p_name, p_bio, p_country) = (presenter.email, presenter.name, presenter.bio, presenter.country)
            else:
                (p_email, p_name, p_bio, p_country) = (user.email, user.name, '', user.country)
            return render_template('submit.html', page=md(base_page, {
                'pagetitle': 'Submit a proposal',
                'data': Markup(submit_form_preface_markup),
                'title': '',
                'session_type': SessionType.session.value,
                'summary': '',
                'audience': SessionAudience.all.value,
                'keywords': '',
                'no_video': False,
                'notes': '',
                'constraints': '',
                'presenter': {
                    'email': p_email,
                    'name': p_name,
                    'is_lead': True,
                    'bio': p_bio,
                    'country': p_country,
                },
                'countries': sorted(countries),
                'submit_label': 'Submit',
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
            'data': 'The following are your current proposals. Click on a list entry to review that proposal and possibly change it should you wish to.',
            'proposals': [{'title': proposal.title, 'id': proposal.id} for proposal in user.proposals]
        }))
    return render_template('general.html', page=md(base_page, {
        'pagetitle': 'My Proposals Failure',
        'year': year,
        'data': 'You must be registered and logged in to discover your current proposals.',
    }))


@app.route('/proposal_update/<int:id>', methods=['GET', 'POST'])
def proposal_update(id):
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
                if not status:
                    # NB This should never be executed.
                    response = jsonify(message)
                    response.status_code = 400
                    return response
                proposal = Proposal.query.filter_by(id=id).first()
                changeset = {}
                for item in ('title', 'summary', 'session_type', 'keywords', 'no_video', 'audience', 'notes', 'constraints'):
                    if item in proposal_data:
                        if item == 'session_type':
                            datum = SessionType(proposal_data[item])
                        elif item == 'audience':
                            datum = SessionAudience(proposal_data[item])
                        else:
                            datum = proposal_data[item]
                        if datum != proposal.__dict__[item]:
                            changeset[item] = datum
                if changeset:
                    Proposal.query.filter_by(id=id).update(changeset)
                assert len(proposal.presenters) == len(proposal_data['presenters'])
                # TODO What about changing of lead?
                for i, presenter in enumerate(proposal.presenters):
                    changeset = {}
                    presenters_data = proposal_data['presenters'][i]
                    for item in ('email', 'name', 'bio', 'country'):
                        if item in presenters_data and presenter.__dict__[item] != presenters_data[item]:
                            changeset[item] = presenters_data[item]
                    if changeset:
                        Presenter.query.filter_by(email=proposal.presenters[i].email).update(changeset)
                db.session.commit()
                if proposal.scores:
                    for score in proposal.scores:
                        send_email_to(
                            score.scorer.email,
                            score.scorer.name,
                            'ACCUConf Proposal {} has been updated'.format(proposal.title),
                            '''
An email to let you know that the ACCUConf proposal:

{}

has been updated by the submitter and you have already scored that proposal.
'''.format(proposal.title)
                        )
                session['just_updated'] = True
                return jsonify('proposal_update_success')
            return render_template('general.html', page=md(base_page, {
                'pagetitle': 'Proposal Update POST Error',
                'data': 'The logged in user is not in database. This cannot happen.',
            }))
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
            'pagetitle': 'Update a proposal',
            'data': Markup(submit_form_preface_markup + '''
</p>
<p>
This page should present all the data of the submission using editable fields.
If you wish to change anything amend the field as needed and click Update.
</p>
<p>
If you do not wish to make any changes just navigate away from this page. There
is no specific button for "leave things as they are" that is the default action.
(Or rather inaction.)
'''),
            'title': proposal.title,
            'session_type': proposal.session_type.value,
            'summary': proposal.summary,
            'audience': proposal.audience.value,
            'keywords': proposal.keywords,
            'no_video': proposal.no_video,
            'notes': proposal.notes,
            'constraints': proposal.constraints,
            'presenter': {
                'email': presenter.email,
                'name': presenter.name,
                'is_lead': proposal_presenter.is_lead,
                'bio': presenter.bio,
                'country': presenter.country,
            },
            'countries': sorted(countries),
            'submit_label': 'Update',
            'proposal_id': id,
        }))
    return render_template('general.html', page=md(base_page, {
        'pagetitle': 'Proposal Update Failure',
        'data': 'You must be registered and logged in to update a proposal.',
    }))


@app.route('/proposal_update_success')
def proposal_update_success():
    check = is_acceptable_route()
    if not check[0]:
        return check[1]
    assert check[1] is None
    if 'just_updated' in session:
        session.pop('just_updated', None)
        return render_template('general.html', page=md(base_page, {
            'pagetitle': 'Proposal Update Successful',
            'data': '''
Thank you, you have successfully updated your proposal for the ACCU {} conference!
If you need to edit it again you can via the 'My Proposal' menu item.
'''.format(year),
        }))
    return render_template('general.html', page=md(base_page, {
        'pagetitle': 'Update Failed',
        'data': 'You must be registered and logged in to submit a proposal.',
    }))
