from django.urls import path
from .views import ReviewListCreateView, ReviewDetailView

urlpatterns=[
    path('product/<int:product_id>/reviews/',ReviewListCreateView.as_view(),name="product-reviews"),
    path('reviews/<int:pk>/',ReviewDetailView.as_view(),name="review-detail")
]