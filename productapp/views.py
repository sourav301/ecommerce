from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializer import ProductSerializer, CategorySerializer, ProductCreateUpdateSerializer
from .models import Product, Category
# Create your views here.

@api_view(['GET'])
def getData(request):
    return Response({"Products":"List of products"})

@api_view(['GET'])
def getCategories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def createCategory(request):
    serializer = CategorySerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(serializer.error_messages,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def createProduct(request):
    serializer = ProductCreateUpdateSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(serializer.error_messages,status=status.HTTP_400_BAD_REQUEST)