from django.urls import path
from . import views

urlpatterns = [
    path('',views.getData),
    path('categories/create/',views.createCategory),
    path('categories/view/',views.getCategories),
    path('products/create/',views.createProduct),
    path('products/view/',views.getProducts),
]