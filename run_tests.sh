#!/bin/sh

pytest tests_api --cov accuconf_api
pytest tests_cfp --cov accuconf_cfp
pytest tests_cfp__selenium --cov accuconf_cfp
npm test
