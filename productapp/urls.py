from django.urls import path
from . import views

urlpatterns = [
    path('',views.getData),
    path('categories/create/',views.createCategory),
    path('categories/view/',views.getCategories),
    path('products/create/',views.createProduct),
    path('products/view/',views.getProducts,name="Get all products"),
    path('products/view/<int:product_id>/',views.getProducts,name="Product description"),
    path('products/<int:product_id>/stockup/',views.stockUp),
    path('products/<int:product_id>/delete/', views.delete_product),

]