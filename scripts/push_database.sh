#!/bin/bash

push_it() {
    source_file=$1
    destination_directory=conference@dennis.accu.org:/srv/$3.$2.accu.org/public/htdocs/
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
}

destination=$1
case $destination in
    test)
        destination_directory_root=testconference
        ;;
    live)
        destination_directory_root=conference
        ;;
    *)
        echo "'$destination' is not a valid source."
        exit 1
        ;;
esac
source_file=$(pwd)/accuconf.db
push_it $source_file $destination_directory_root cfp
push_it $source_file $destination_directory_root api
