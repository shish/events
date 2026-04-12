# Events Index

I want to know about events that are relevant to my interests, and have them automatically added to my google calendar


# Quickstart

Open in visual studio code and accept the prompt to use a devcontainer, or use github's online IDE:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/shish/events)

Once the IDE is open, `flask --app events:create_app --debug run` to start backend and frontend at once.

A built-in browser in the IDE should open automatically, with hot-reloading configured for both backend and frontend code.


# Slowstart

Install:
```
uv run flask --app events:create_app init-db
```

Run:
```
uv run flask --app events:create_app --debug run
```

Test:
```
uv run ruff check
uv run ruff format
uv run ty check
uv run pytest
```
