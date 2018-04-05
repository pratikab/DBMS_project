#!/bin/sh
rm db.sqlite3
python manage.py migrate
python manage.py populatedb
python manage.py runserver
