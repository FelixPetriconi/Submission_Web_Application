#!/bin/sh

pytest tests_api --cov accuconf_api  --cov-report html:cov_html_accuconf_api
pytest tests_cfp --cov accuconf_cfp --cov-report html:cov_html_accuconf_cfp
pytest tests_cfp__selenium --cov accuconf_cfp  --cov-report html:cov_html_accuconf_cfp__selenium
npm test
