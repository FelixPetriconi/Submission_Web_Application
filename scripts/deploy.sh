#!/bin/sh

echo_usage() {
    echo "Usage: deploy.sh (cfp|api).(testconference|conference)"
}

if [ $# -ne 1 ]; then
    echo_usage
    exit
fi

case $1 in
    cfp.testconference | cfp.conference )
        chmod -R go+rX accuconf*
        destination=conference@dennis.accu.org:/srv/$1.accu.org/public/htdocs/
        rsync -rav --delete  --exclude=__pycache__/ accuconf $destination
        scp accuconf.wsgi $destination
        ;;
    api.testconference | api.conference )
        chmod -R go+rX accuconf_api
        destination=conference@dennis.accu.org:/srv/$1.accu.org/public/htdocs/
        rsync -rav --delete  --exclude=__pycache__/ accuconf_api $destination
        scp accuconf_api.wsgi $destination
        ;;
    *)
        echo_usage
        ;;
esac
