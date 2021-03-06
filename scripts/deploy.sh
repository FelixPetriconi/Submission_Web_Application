#!/bin/sh

echo_usage() {
    echo "Usage: deploy.sh (cfp|api).(testconference|conference)"
}

if [ $# -ne 1 ]; then
    echo_usage
    exit
fi

# NB accuconf_cfp is the primary application and should be copied to the deployment area in archive mode.
# accuconf_api relies on some files in accuconf_cfp by symbolic link and so cannot use archive mode – the
# deployment areas are self-contained so cannot have symbolic links.

case $1 in
    cfp.testconference | cfp.conference )
        chmod -R go+rX accuconf*
        destination=conference@dennis.accu.org:/srv/$1.accu.org/public/htdocs/
        rsync -av --delete  --exclude=__pycache__/ accuconf_cfp models cli.sh test_utils emailouts accuconf_api_config_available.py accuconf_cfp_config_administeringDatabase.py accuconf_cfp_config_callOpen.py accuconf_cfp_config_maintenance.py accuconf_cfp_config_reviewingOnly.py pip_runtime_requirements.txt pip_admin_requirements.txt pip_test_requirements.txt $destination
        rsync -av --delete  --exclude=__pycache__/ scripts/cli_commands.py $destination/scripts
        scp accuconf_cfp.wsgi $destination
        ;;
    api.testconference | api.conference )
        chmod -R go+rX accuconf_api
        destination=conference@dennis.accu.org:/srv/$1.accu.org/public/htdocs/
        rsync -rLptgov --delete  --exclude=__pycache__/ accuconf_api models $destination
        scp accuconf_api.wsgi $destination
        ;;
    *)
        echo_usage
        ;;
esac
