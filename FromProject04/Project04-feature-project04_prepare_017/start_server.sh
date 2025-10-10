#!/bin/bash
cd /home/runner/workspace
exec poetry run python manage.py runserver 0.0.0.0:5000
