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


@pytest.fixture(scope="session")
def server():
    process = subprocess.Popen('python3 {}'.format(this_directory / 'start_server.py'), shell=True)
    time.sleep(2)  # Need a short while for the server to settle, 0.5 works locally but Travis-CI needs longer.
    process.poll()
    assert process.returncode is None, process.returncode
    yield
    process.poll()
    assert process.returncode is None, process.returncode
    process.kill()
    time.sleep(0.5)  # We need to give the OS chance to kill the process.
    process.poll()
    assert process.returncode == -9, process.returncode


@pytest.fixture
def browser():
    driver = webdriver.PhantomJS()
    yield driver
    driver.quit()
