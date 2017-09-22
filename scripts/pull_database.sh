#!/bin/bash

source=$1
case $source in
    test)
        source_directory=cfp.testconference.accu.org
        ;;
    live)
        source_directory=cfp.conference.accu.org
        ;;
    *)
        echo "'$source' is not a valid source."
        exit 1
        ;;
esac
source_file=conference@dennis.accu.org:/srv/$source_directory/public/htdocs/accuconf.db
destination_directory=$(pwd)
scp $source_file $destination_directory
