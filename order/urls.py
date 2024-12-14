from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.get_or_create_cart, name='get_or_create_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/view/', views.view_cart, name='view_cart'),
    path('orders/place-from-cart/', views.place_order_from_cart, name='place_order_from_cart'),
]