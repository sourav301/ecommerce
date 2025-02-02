An scalable ecommerce website backend written using Django REST Framework.

- Start the docker
docker compose up web db adminer redis

- Start only django web framework
python manage.py runserver


The following services are available

categories - create,view
products - create,view,stockup,delete

cart - add,view,delete
orders - view,checkout
payment - update

