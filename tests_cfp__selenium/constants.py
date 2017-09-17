import os

if 'TRAVIS' in os.environ and os.environ['TRAVIS']:
    driver_wait_time = 4
else:
    driver_wait_time = 2
