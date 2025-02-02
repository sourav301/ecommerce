from django.contrib import admin
from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('login',views.login),
    re_path('signup',views.signup),
    re_path('test_token',views.test_token),
    path('',include('productapp.urls')),
    path('', include('blog.urls')),  
    path('', include('order.urls')),  
    path('', include('reviews.urls'))
]
