#!/bin/sh

export FLASK_APP=./scripts/cli_commands.py
exec flask $*
