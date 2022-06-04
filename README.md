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

### Load initial data
    python manage.py loaddata initial_store_items.json wishlist_status.json

### Start server
    python manage.py runserver