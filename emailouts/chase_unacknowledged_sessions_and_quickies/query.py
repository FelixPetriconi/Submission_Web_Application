from models.proposal import Proposal
from models.proposal_types import ProposalState, SessionType


def query():
    proposals = Proposal.query.filter_by(status=ProposalState.accepted)
    proposals = [p for p in proposals if p.session_type != SessionType.fulldayworkshop]
    assert all(p.session_type in (SessionType.session, SessionType.miniworkshop, SessionType.workshop, SessionType.quickie) for p in proposals)
    proposals = [p for p in proposals if p.status == ProposalState.accepted]
    return tuple((p, p.proposer) for p in proposals)


def edit_template(template_path, proposal, person):
    with open(template_path) as template_file:
        return template_file.read().strip().format(person.name, proposal.session_type.value, proposal.title)
