import os

if 'TRAVIS' in os.environ and os.environ['TRAVIS']:
    driver_wait_time = 2
else:
    driver_wait_time = 1
