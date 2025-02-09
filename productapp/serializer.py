from rest_framework import serializers
from .models import Category, Product, ProductImage

from django.core.exceptions import ValidationError

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

   
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True)  # Use many=True to handle multiple images
    class Meta:
        model = Product
        fields = '__all__'

    
class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'category']

class StockUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value = 1)
 
class ProductImagesCreateSerializer(serializers.Serializer):
    images = serializers.ListField(
        child=serializers.ImageField(),  # List of image fields
        required=False
    )

    def create(self, validated_data):
        images = validated_data.get('images', [])
        product = self.context['product']  # Assuming product passed in context
        product_images = []
        for image in images:
            product_images.append(ProductImage.objects.create(product=product, image=image))
        
        return product_images