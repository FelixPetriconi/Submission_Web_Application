#!/bin/sh

for directory in tests_api tests_cfp tests_cfp__selenium
do
    pytest $directory
done
npm test
