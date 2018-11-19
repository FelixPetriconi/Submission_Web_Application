import pytest

# Apparently unused but loading has crucial side effects
import configure

from test_utils.fixtures import get_registrant

#  It used to be possible to call fixtures as normal Python functions, and this was
# useful and used. However, this is now not allowed by PyTest, so use this "define
# a getter and create a fixture" approach so as to provide both functions and fixtures.


def get_registrant_without_cpassphrase():
    r = get_registrant()
    del r['cpassphrase']
    return r


@pytest.fixture
def registrant():
    return get_registrant_without_cpassphrase()
