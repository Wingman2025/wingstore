web: gunicorn wingstore.wsgi
release: python manage.py migrate && python manage.py collectstatic --noinput && python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='jorge').exists() or User.objects.create_superuser('jorge', 'jorge@gmail.com', '1234tarifa@')"
