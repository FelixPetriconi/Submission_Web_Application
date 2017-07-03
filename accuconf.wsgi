# -*- mode: python; -*-

activate_this = '/srv/conference.accu.org/Python3/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(abspath(__file__)))

from accuconf import app as application
