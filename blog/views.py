from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from .models import Blog
from .serializers import BlogSerializer

class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by('-created_at')  # Most recent first
    serializer_class = BlogSerializer
    