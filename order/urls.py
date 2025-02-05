from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.get_or_create_cart, name='get_or_create_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/delete/', views.delete_from_cart, name='delete_from_cart'),
    path('cart/view/', views.view_cart, name='view_cart'),
    path('orders/checkout/', views.place_order_from_cart, name='checkout'),
    path('orders/view/', views.view_orders, name='view_orders'),
    path('orders/view/<user_id>', views.view_orders, name='view_orders'),
    path('payment/<int:payment_id>/update/', views.update_payment_status, name='update_payment_status'),

    
]