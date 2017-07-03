#!/bin/sh

echo_usage() {
    echo "Usage: deploy.sh (testconference|conference)"
}

if [ $# -ne 1 ]; then
    echo_usage
    exit
fi

case $1 in
    testconference | conference )
        chmod -R go+rX accuconf*
        rsync -rav --delete  --exclude=__pycache__/ accuconf accuconf.wsgi conference@dennis.accu.org:/srv/cfp.$1.accu.org/public/htdocs/
        ;;
    *)
        echo_usage
        ;;
esac
