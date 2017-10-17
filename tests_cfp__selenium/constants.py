import os

if 'TRAVIS' in os.environ and os.environ['TRAVIS']:
    driver_wait_time = 5
else:
    driver_wait_time = 2
