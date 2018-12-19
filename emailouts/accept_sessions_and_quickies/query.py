from models.proposal import Proposal
from models.proposal_types import ProposalState, SessionType


def query():
    proposals = Proposal.query.filter_by(status=ProposalState.accepted)
    proposals = [p for p in proposals if p.session_type != SessionType.fulldayworkshop]
    assert all(p.session_type in (SessionType.session, SessionType.workshop, SessionType.longworkshop, SessionType.quickie) for p in proposals)
    return tuple((p, p.proposer) for p in proposals)


def edit_template(template_path, proposal, person):
    with open(template_path) as template_file:
        return template_file.read().strip().format(person.name, proposal.session_type.value, proposal.title,
"""
As this session is a quickie, the conference is not able to provide the
'presenter package' for putting on this session, the presenter will have to
register for the conference via the usual route – but we are trying to
ensure there is a registration discount for quicker presenters.
""" if proposal.session_type == SessionType.quickie else """
As this is a full session, the presenter, or lead presenter for multi-
presenter sessions, will be offered a 'presenter deal' of free conference
ticket, contribution to travel expenses, and two nights accommodation at
the conference hotel.

See https://conference.accu.org/lead_presenter_deals.html
""")
