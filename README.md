Events Index
============

I want to know about events that are relevant to my interests, and have them automatically added to my google calendar

Quickstart:
===========
Open in visual studio code and accept the prompt to use a devcontainer, or use github's online IDE:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/shish/events)

Once the IDE is open, `cd frontend && npm run all` to start backend and frontend at once.

A built-in browser in the IDE should open automatically, with hot-reloading configured for both backend and frontend code.


Slowstart
=========
Build frontend:
---------------
```
cd frontend
npm install
npm run dev    # for debugging
npm run build  # for prod
```

Backend:
--------
```
python3 -m venv venv
./venv/bin/pip install -e .
./venv/bin/flask --app backend.app init-db  # create a database with example data
./venv/bin/flask --app backend.app run --port 8000 --debug            # for debugging
./venv/bin/gunicorn -w 4 'backend.app:create_app()' -b 0.0.0.0:8000   # for prod
```
