#!/bin/bash
export PYTHONPATH="${PYTHONPATH}:/app"
export FLASK_APP=app.py
export FLASK_ENV=production
python app.py