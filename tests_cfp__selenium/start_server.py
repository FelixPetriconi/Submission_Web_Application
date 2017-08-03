import pathlib
import sys

from configuration import host, port

sys.path.insert(0, str(pathlib.PurePath(__file__).parent.parent))

from accuconf_cfp import app, db

app.config['CALL_OPEN'] = True
app.config['REVIEWING_ALLOWED'] = True
app.config['MAINTENANCE'] = False

db.drop_all()
db.create_all()

app.run(host=host, port=port, debug=False)
