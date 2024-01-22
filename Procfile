web: gunicorn pro.wsgi
release: python manage.py makemigrations users --noinput
release: python manage.py makemigrations review --noinput
release: python manage.py makemigrations records --noinput
release: python manage.py makemigrations Profile --noinput
release: python manage.py makemigrations menu --noinput
release: python manage.py makemigrations payments --noinput
release: python manage.py makemigrations chatbox --noinput
release: python manage.py collectstatic --noinput
release: python manage.py migrate --noinput 