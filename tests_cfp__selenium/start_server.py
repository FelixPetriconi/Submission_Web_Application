import pathlib
import sys

import common

sys.path.insert(0, str(pathlib.PurePath(__file__).parent.parent))

from accuconf_cfp import app, db

app.config['CALL_OPEN'] = True
app.config['REVIEWING_ALLOWED'] = True
app.config['MAINTENANCE'] = False

db.drop_all()
db.create_all()

app.run(host=common.host, port=common.port, debug=False)
