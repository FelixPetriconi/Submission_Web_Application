from models.user import User


def query():
    users = User.query.all()
    return tuple((p, u) for u in users for p in u.proposals)


def edit_template(template_path, proposal, person):
    with open(template_path) as template_file:
        return template_file.read().strip().format(person.name, proposal.title)
