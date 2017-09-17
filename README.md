[![GPLv3](https://img.shields.io/badge/license-GPL_3-green.svg)](https://www.gnu.org/licenses/gpl-3.0.en.html)
[![Build Status](https://travis-ci.org/ACCUConf/ACCUConf_Submission_Web_Application.svg?branch=master)](https://travis-ci.org/ACCUConf/ACCUConf_Submission_Web_Application)
[![Coverage Status](https://coveralls.io/repos/github/ACCUConf/ACCUConf_Submission_Web_Application/badge.svg?branch=master)](https://coveralls.io/github/ACCUConf/ACCUConf_Submission_Web_Application)

# ACCUConf Web Applications

This repository contains the source of the Web application for submitting and
reviewing [ACCU conference](https://conference.accu.org) session proposals, and also the Web application for
a personalised schedule for use leading up to and during the conference. The two Web applications
are [Flask](http://flask.pocoo.org/)/[SQLAlchemy](https://www.sqlalchemy.org/)/SQLite applications with a
shared data model, and shared utilities.

The submission application:

1. Allows people to register as users.
1. Allows registered users to login and submit and amend session proposals.
1. Allows registered users who are designated reviewers to review the submitted proposals.

The schedule application provides a RESTful API to access the final conference schedule data. The API is
designed for
the [ACCU schedule web application](https://github.com/ACCUConf/ACCUConf_Schedule_Web_Application). The API
is public so any other application can use it.

The submission application is deployed to https://cfp.conference.accu.org, the schedule application is
deployed to https://api.conference.accu.org. The submission applications will only be active during the
"call for proposals" of a given year, and the schedule API application will only be available once the
schedule is finalised up to the end of the conference for that year.

## Contributing

Contributions are welcome from anyone and everyone who believes they have something constructive to
contribute.

First step is to clone the repository so as to be able to run the applications. Second step is to make sure
all the necessary Python bits and pieces are installed. The files _pip\_runtime\_requirements.txt_,
_pip\_test\_requirements.txt_, and  _pip\_admin\_requirements.txt_ contain lists of the packages
required. It may be that your platform has all of these or allows them to be installed. Otherwise the best
approach is to use pip to install. Many people will use a virtual environment, in which case:

    pip install --upgrade -r pip_runtime_requirements.txt

will install all the packages needed for running the applications. For testing install the test requirements
as well. The admin requirements are for using the scaffolded admin interface to work on the database.

With everything installed, a database is needed. Executing:

    ./cli.sh db_init

should do the needful.

Running the submission application is then a matter of executing:

    ./run_cfp.py

This should set the submission application running on localhost:8000. The state of the application is
determined at application start time. The default is the "off" state, so should just put up a "not open"
message. To get the application into the "open" state you need to have a file _accuconf\_config.py_ in place
before starting the application. This file should have the line:

    from models.configuration import CallForProposalsOpen as Config

Once set up chip in with issues and, if you are willing, pull requests.

These two applications are relatively straightforward, relatively small [Flask](http://flask.pocoo.org/)
applications using [SQLAlchemy](https://www.sqlalchemy.org/) and SQLite. There are the _accuconf\_cfp_ and
_accuconf\_api_ packages which are the two applications, and the _models_ and _utils_ packages which are the
shared packages for the two applications. [Jinja2](http://jinja.pocoo.org/docs/2.9/) templating is used for
rendering.

Tests are [pytest](https://docs.pytest.org/en/latest/) ones. Unit tests (exercising the route controllers)
are in _tests\_cfp_, whilst _tests\_cfp\_\_selenium_ holds the webdriver driven tests. The latter use
_chromedriver_ so you will need to ensure you have that installed. PhantomJS appears not to be up to the job
of being a headless driver for these tests hence using Chromedriver in headless mode.

Running:

    ./run_tests.sh

should run all of the tests and create coverage reports in _cov\_html\_accuconf\_api_,
_cov\_html\_accuconf\_cfp, and _cov\_html\_accuconf\_cfp\_\_selenium_.

## Historical note

This is a complete rewrite of the application used for ACCU 2017, based on an evolution of the data model
used then.

## Licence

This code is licensed under
the [GNU Public License Version 3](https://www.gnu.org/licenses/gpl-3.0.en.html).
