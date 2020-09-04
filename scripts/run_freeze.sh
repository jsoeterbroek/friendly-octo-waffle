#!/bin/bash

gunicorn --bind 0.0.0.0:8000 app.wsgi:application --daemon

python3 manage.py generate_static_site



