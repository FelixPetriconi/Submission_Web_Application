"""
Various configurations for a cfp application test.
"""

import sys

#  Tests are not always initiated from the top level of the project. Ensure that
# directory is in the path so that imports work.
from pathlib import PurePath

path_to_add = str(PurePath(__file__).parent.parent)
if path_to_add not in sys.path:
    sys.path.insert(0, path_to_add)

# Apparently unused but has crucial side effects.
import accuconf_cfp
