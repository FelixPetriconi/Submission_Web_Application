from models.proposal import Proposal
from models.proposal_types import ProposalState, SessionType


def query():
    proposals = Proposal.query.filter_by(status=ProposalState.acknowledged)
    proposals = tuple(p for p in proposals if p.session_type == SessionType.session or p.session_type == SessionType.quickie)
    return tuple((None, proposal.proposer) for _, proposal in {p.proposer.name: p for p in proposals}.items())


def edit_template(template_path, proposal, person):
    with open(template_path) as template_file:
        return template_file.read().strip().format(person.name)
