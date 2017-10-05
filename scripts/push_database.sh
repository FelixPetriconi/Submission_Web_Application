#!/bin/bash

destination=$1
case $destination in
    test)
        destination_directory=cfp.testconference.accu.org
        ;;
    live)
        destination_directory=cfp.conference.accu.org
        ;;
    *)
        echo "'$destination' is not a valid source."
        exit 1
        ;;
esac
source_file=$(pwd)/accuconf.db
destination_directory=conference@dennis.accu.org:/srv/$destination_directory/public/htdocs/
echo -n "
About to push:  $source_file
to:  $destination_directory

is this OK? "
read answer
echo ""
if [ x$answer = xyes ]; then
    scp $source_file $destination_directory
else
    echo "No action taken."
fi
