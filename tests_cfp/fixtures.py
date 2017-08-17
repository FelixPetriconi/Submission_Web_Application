import pytest

# Apparently unused but loading has crucial side effects
import configure

from test_utils.fixtures import registrant as central_registrant


@pytest.fixture
def registrant():
    c_r = central_registrant()
    del c_r['cpassphrase']
    return c_r
