# -*- mode: python; -*-

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from accuconf_api import app as application
