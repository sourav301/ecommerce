from rest_framework import serializers
from .models import Category, Product, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

   
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['product','image']

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
 