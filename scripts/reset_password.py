#!/usr/bin/env python3

"""
This is the script to reset the password of a registered user.
"""

import hashlib
import sys

from pathlib import Path

from sqlalchemy import create_engine, MetaData, Table, and_, or_, select


def _get_user(engine, table, email):
    item = tuple(engine.execute(table.select(table.c.user_id == email)))
    length = len(item)
    if length == 0:
        print('user {} not found.'.format(email))
        sys.exit(3)
    elif length == 1:
        return item[0]
    else:
        print('Found multiple instances of the email address:')
        for i in item:
            print('\t{}'.format(i))
        sys.exit(3)


def set_password_of_user(db_path, email, password):
    """
    Find the user record and reset the password.
    """
    engine = create_engine('sqlite:///' + str(db_path.absolute()))
    tables = engine.table_names()
    table_name = 'users'
    if table_name not in tables:
        print('Database file, {}, does not contain a {} table.'.format(db_path, table_name))
        sys.exit(2)
    users = Table(table_name, MetaData(), autoload=True, autoload_with=engine)
    person = _get_user(engine, users, email)
    print('Amending password for the following user:\n\t{}'.format(person))
    engine.execute(users.update().where(users.c.user_id == email).values(user_pass=hashlib.sha256(password.encode('utf-8')).hexdigest()))
    new_person = _get_user(engine, users, email)
    print('Amended record:\n\t{}'.format(new_person))


def main(args):
    if len(args) != 3:
        print('Usage: {} <database-file> <email-address> <password>'.format(Path(__file__).name))
        sys.exit(1)
    db_path = Path(args[0])
    if not db_path.is_file():
        print('Database file, {}, does not exist.'.format(db_path))
        sys.exit(1)
    set_password_of_user(db_path, *args[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
