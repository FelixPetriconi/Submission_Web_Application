"""
Various bits of code used in various places. It is assumed this file is imported into all tests.
"""

import pytest
import pathlib
import subprocess
import time

from selenium import webdriver

this_directory = pathlib.PurePath(__file__).parent

host = 'localhost'
port = '65530'

base_url = 'http://{}:{}/'.format(host, port)


@pytest.fixture(scope='module', autouse=True)
def server():
    # NB do not spawn with a shell since then you can't terminate the server.
    process = subprocess.Popen(('python3', '{}'.format(this_directory / 'start_server.py')))
    time.sleep(2)  # Need a short while for the server to settle, 0.5 works locally but Travis-CI needs longer.
    process.poll()
    assert process.returncode is None, 'Server start return code {}'.format(process.returncode)
    yield
    process.poll()
    assert process.returncode is None, 'Server used return code P{.'.format(process.returncode)
    process.terminate()
    process.wait()
    assert process.returncode == -15, 'Server terminated return code {}.'.format(process.returncode)


@pytest.fixture
def browser():
    driver = webdriver.PhantomJS()
    yield driver
    driver.quit()
