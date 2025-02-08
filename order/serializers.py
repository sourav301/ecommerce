from rest_framework import serializers
from .models import Product, Cart, CartItem, Order, OrderItem, Payment


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
    def validate_quantity(self, value):
        return int(value)

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    category_name = serializers.CharField(source='product.category.name')
    class Meta:
        model = OrderItem
        fields = ['product_name', 'category_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['id','username', 'items', 'status', 'created_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['status']
        read_only_fields = ['order']