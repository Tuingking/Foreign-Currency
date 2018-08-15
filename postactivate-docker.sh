#!/bin/sh

flask deploy
FLASK_ENV=production flask run --host=0.0.0.0