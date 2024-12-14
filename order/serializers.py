from rest_framework import serializers
from .models import Product, Cart, CartItem


# Serializer for CartItem model
class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()


    class Meta:
        model = CartItem
        fields = ['product', 'quantity']
    
    def get_product(self, obj):
        # You can return only specific fields of the product here
        product = obj.product
        return {
            'name': product.name,
            'description': product.description
        }

# Serializer for Cart model
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['user', 'items']