#!/usr/bin/env bash
exec gunicorn nova_project.wsgi:application --bind 0.0.0.0:${PORT:-8000}
