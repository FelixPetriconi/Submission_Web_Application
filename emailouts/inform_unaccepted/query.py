from models.proposal import Proposal
from models.proposal_types import ProposalState


def query():
    proposals = Proposal.query.filter_by(status=ProposalState.submitted)
    return tuple((p, p.proposer) for p in proposals)


def edit_template(template_path, proposal, person):
    with open(template_path) as template_file:
        return template_file.read().strip().format(person.name, proposal.session_type.value, proposal.title)
