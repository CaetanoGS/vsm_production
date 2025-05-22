#!/bin/sh

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for PostgreSQL..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
      sleep 1
    done

    echo "PostgreSQL started"
fi

# Apply migrations and run server
if [ "$DJANGO_MODE" = "production" ]; then
    echo "Running Production Server"
    
    python manage.py migrate
    if [ $? -ne 0 ]; then
      echo "Error: migrate failed."
      exit 1
    fi

    echo "Migrations completed successfully."
    gunicorn vsm_tb.wsgi:application --bind 0.0.0.0:8001
else
    echo "Running Development Server"
    python manage.py makemigrations
    if [ $? -ne 0 ]; then
      echo "Error: makemigrations failed."
      exit 1
    fi
    
    python manage.py migrate
    if [ $? -ne 0 ]; then
      echo "Error: migrate failed."
      exit 1
    fi

    echo "Migrations completed successfully."
    python manage.py runserver 0.0.0.0:8000
fi
