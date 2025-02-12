from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .serializer import ProductSerializer, CategorySerializer, ProductCreateUpdateSerializer, StockUpdateSerializer,ProductImagesCreateSerializer
from .models import Product, Category, ProductImage
from rest_framework.parsers import MultiPartParser, FormParser

from rest_framework.decorators import parser_classes

from rest_framework.permissions import IsAuthenticated
from server.permissions import IsStockManager
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
def getProducts(request, product_id=None):
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": f"Product with ID {product_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)
    else:
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsStockManager])
def createCategory(request):
    serializer = CategorySerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(serializer.error_messages,status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsStockManager])
def createProduct(request): 

    serializer = ProductCreateUpdateSerializer(data = request.data)
    # category_id = request.data.get("category")
    # try:
    #     category_exists = Category.objects.get(id=category_id)
    # except Category.DoesNotExist:
        # return Respnse({"error": "Category with this ID does not exist."}, status=status.HTTP_400_BAD_REQUEST)

    if serializer.is_valid():
        category_id = serializer.validated_data.get('category')
        
        # Check if the category exists in the database
        if not Category.objects.filter(id=category_id.id).exists():
            return Response(
                {"detail": "Category does not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product = serializer.save() 
        data = serializer.data
        parser_classes = [MultiPartParser] 
        serializer = ProductImagesCreateSerializer(data=request.data,context={'product': product})
        if serializer.is_valid():
            serializer.create(validated_data=serializer.validated_data) 
        
        return Response(data,status=status.HTTP_201_CREATED)
    return Response(serializer.error_messages,status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def stockUp(request,product_id):
    serializer = StockUpdateSerializer(data = request.data)
    if serializer.is_valid():
        quantity = serializer.validated_data['quantity']

        try:
            product = Product.objects.get(id = product_id)
            product.stock += quantity
            product.save()

            return Response({
                "message": "Stock updated successfully.",
                "product_id": product.id,
                "new_stock": product.stock,
            }, status=status.HTTP_200_OK)
        
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)


    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_product(request, product_id):
    try:
        # Find the product by ID
        product = Product.objects.get(id=product_id)
        
        # Delete the product
        product.delete()

        return Response({
            "message": f"Product with ID {product_id} has been deleted successfully."
        }, status=status.HTTP_200_OK)
    
    except Product.DoesNotExist:
        return Response({
            "error": f"Product with ID {product_id} does not exist."
        }, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])  # To parse multipart form data
def upload_product_image(request):
    """
    Upload image for a specific product and return the image URL.
    """
    # Check if the product exists
    try:
        product = Product.objects.get(id=request.data.get('product_id'))
    except Product.DoesNotExist:
        return Response({"detail": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get the image files from the request data
    image_files = request.FILES.getlist('images')  # 'images' is the field name for multiple images

    if not image_files:
        return Response({"detail": "No images provided."}, status=status.HTTP_400_BAD_REQUEST)

    image_urls = []
    
    # Loop through the image files and create ProductImage objects
    for image_file in image_files:
        product_image = ProductImage.objects.create(product=product, image=image_file)
        image_urls.append(product_image.image.url)
    
    # Return the URLs of the uploaded images
    return Response({"image_urls": image_urls}, status=status.HTTP_201_CREATED)