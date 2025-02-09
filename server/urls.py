from django.contrib import admin
from django.urls import path, re_path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('login',views.login,name="login"),
    re_path('signup',views.signup,name="register"),
    re_path('test_token',views.test_token,name="Test token"),
    path('',include('productapp.urls')),
    path('', include('blog.urls')),  
    path('', include('order.urls')),  
    path('', include('reviews.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)