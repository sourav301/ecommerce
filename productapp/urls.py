from django.urls import path
from . import views

urlpatterns = [
    path('',views.getData),
    path('categories/create/',views.createCategory,name="Create Category"),
    path('categories/view/',views.getCategories,name="Get Category"),
    path('products/create/',views.createProduct,name="Create Product"),
    path('products/view/',views.getProducts,name="Get all products"),
    path('products/view/<int:product_id>/',views.getProducts,name="Product description"),
    path('products/<int:product_id>/stockup/',views.stockUp),
    path('products/<int:product_id>/delete/', views.delete_product),

]