#!/usr/bin/env bash
set -o errexit

python manage.py migrate --no-input
gunicorn flota.wsgi:application --timeout 600
