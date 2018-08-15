#!/bin/sh

export FLASK_APP="wsgi.py"
export FLASK_DEBUG=1
export FLASK_CONFIG="dev"

FLASK_ENV=development flask run --host=0.0.0.0