"""
Various fixtures used in the test modules.
"""

import pytest
import pathlib
import subprocess
import time

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


@pytest.fixture(scope='module', autouse=True)
def server():
    """A fixture to start a new server.

    It is assumed that a new server is started for each test module.
    """
    # NB do not spawn with a shell since then you can't terminate the server.
    process = subprocess.Popen(('python3', '{}'.format(pathlib.PurePath(__file__).parent / 'start_server.py')))
    time.sleep(1.5)  # Need a short while for the server to settle, 0.5 works locally but Travis-CI needs longer.
    process.poll()
    assert process.returncode is None, 'Server start return code {}'.format(process.returncode)
    yield
    process.poll()
    assert process.returncode is None, 'Server terminated return code {}.'.format(process.returncode)
    process.terminate()
    process.wait()
    assert process.returncode == -15, 'Server terminated return code {}.'.format(process.returncode)


@pytest.fixture(scope='module')
def driver():
    # It seems that PhantomJS cannot handle the button clicking.
    # wd = webdriver.PhantomJS()
    # It seems geckodriver cannot work headless easily.
    # wd = webdriver.Firefox()
    # So we end up associating with the Borg.
    capabilities = DesiredCapabilities.CHROME
    capabilities['loggingPrefs'] = {
        'browser': 'ALL',
        # 'driver': 'ALL',
    }
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    wd = webdriver.Chrome(chrome_options=options, desired_capabilities=capabilities)
    yield wd
    print('Browser', wd.get_log('browser'))
    # print('Driver', wd.get_log('driver'))
    wd.quit()
