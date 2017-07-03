#!/usr/bin/env python3

import sys

from accuconf import app

if len(sys.argv) > 1:
    host = sys.argv[1]
else:
    host = 'localhost'
app.run(host=host, port=8000, debug=True)
