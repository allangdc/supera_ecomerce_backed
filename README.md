# Supera E-Commerce Backend

## Setup system
### Initialization of the Virtual Environment
    python3 -m venv .venv
    source .venv/bin/activate

### Install requirement packages
    pip install -r requirements.txt

### Create database
    python manage.py makemigrations
    python manage.py migrate

### Start server
    python manage.py runserver