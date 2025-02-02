- Create a app
python manage.py startapp reviews

- Add to INSTALLED_APPS in settings.py

- Update models.py
python manage.py makemigrations reviews
python manage.py migrate

- Update serializer.py
- Update views.py
- Update urls.py