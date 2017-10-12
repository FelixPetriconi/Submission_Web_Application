"""Various utility functions.

A collection of functions used by various route controllers. The route controllers
are in separate modules hence pulling these functions out into a separate module.
"""

import hashlib
import os
import re

from email.mime.text import MIMEText
from email.utils import formatdate
from pathlib import Path
from smtplib import SMTP

from flask import redirect, session

from accuconf_cfp import app, countries


def hash_passphrase(text):
    """Function for 'encrypting' a passphrase before putting it into the database."""
    return hashlib.sha512(text.encode('utf-8')).hexdigest()


def is_acceptable_route():
    """Check the state of the application and return a pair.

    The first item of the pair is a Boolean stating whether the route is acceptable.
    The second item of the pair is a rendered template to display if the route is not
     allowed, and None if it is.
    """
    if app.config['MAINTENANCE']:
        return False, redirect('/')
    if not app.config['CALL_OPEN']:
        if app.config['REVIEWING_ALLOWED']:
            return True, None
        return False, redirect('/')
    return True, None


def is_logged_in():
    """Predicate to determine if a user is logged in.

    On logging in a record is placed into the session data structure with key 'email'.
    The record is removed on logout.
    """
    return 'email' in session and bool(session['email'])


def is_valid_email(email):
    """A purported email address in in valid format."""
    return bool(re.compile(r'^([a-zA-Z0-9_.+-])+@(([a-zA-Z0-9-_])+\.)+([a-zA-Z0-9])+$').search(email))


def is_valid_passphrase(passphrase):
    """Passphrases are required to be eight or more characters."""
    return len(passphrase) >= 8


def is_valid_name(name):
    """Names are required to be 2 or more characters."""
    return len(name) > 1


def is_valid_bio(bio):
    """Bios must be at least 40 characters."""
    return len(bio) > 40


def is_valid_phone(phone):
    """Phone numbers are required to conform to ITU rules."""
    return bool(re.compile(r'^\+?[0-9 ]+$').search(phone))


def is_valid_country(country):
    """The country must be from the current official list as per pycountry."""
    return country in countries


#  This code has to work on Python 3.4, so cannot use the lovely Python 3.5 and later stuff.
#  Must have the ability to merge two dictionaries, but no 3.5 stuff so this for 3.4.
def md(a, b):
    """Merge two dictionaries into a distinct third one."""
    rv = a.copy()
    rv.update(b)
    return rv


def send_email_to(email_address, name, subject, text, trial=True):
    """Send an email to someone for some reason using the ACCU mail server via
     the conference@accu.org email account."""

    def send_email():
        message = MIMEText(text, _charset='utf-8')
        message['From'] = 'ACCUConf <conference@accu.org>'
        if trial:
            message['To'] = 'Russel Winder <russel@winder.org.uk>'
        else:
            message['To'] = name + '<' + email_address + '>'
            message['Cc'] = 'ACCUConf <conference@accu.org>'
        message['Subject'] = subject
        message['Date'] = formatdate()  # RFC 2822 format.
        server.send_message(message)

    if trial:
        with SMTP('smtp.winder.org.uk') as server:
            send_email()
    else:
        with SMTP('mail.accu.org') as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            with open(str(Path(os.environ['HOME']) / '.accuconf' / 'passphrase')) as passphrase_file:
                server.login('conference', passphrase_file.read().strip())
            send_email()

