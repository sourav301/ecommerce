from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem, Product, Order, OrderItem
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import CartSerializer, CartItemSerializer

from django.db import transaction

# Ensure the user has a cart, if not, create one
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_or_create_cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    
    # Serialize the cart and return it
    serializer = CartSerializer(cart)
    return Response(serializer.data)

@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    user = request.user
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)

    try:
        # Get the user's cart (create if it doesn't exist)
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        # Create a new cart if it doesn't exist
        cart = Cart.objects.create(user=user)

    try:
        # Get the product object
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    if quantity>product.stock:
        return Response({"detail": f"Not enough stock. Please select less than {product.stock}"}, status=status.HTTP_404_NOT_FOUND)
    # Try to get the CartItem object, or create it if it doesn't exist
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        # If the item already exists, update the quantity
        cart_item.quantity += quantity
        cart_item.save()
        return Response({
            "message": "Item quantity updated",
            "cart_item": CartItemSerializer(cart_item).data
        }, status=status.HTTP_200_OK)
    else:
        cart_item.quantity = quantity
        cart_item.save()
    # If the item was created, return the response
    return Response({
        "message": "Item added to cart",
        "cart_item": CartItemSerializer(cart_item).data
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def view_cart(request):
    user = request.user
    try:
        cart = Cart.objects.get(user=user)
        cart_items = cart.items.all()
        data = [{"product_id":item.product.id,
                   "product_name":item.product.name,
                   "quantity":item.quantity,
                   "total_price":item.product.price*item.quantity} 
                  for item in cart_items]
        return Response(data,status=status.HTTP_200_OK)

    except Cart.DoesNotExist:
        return Response({'error','No items in cart'},status = status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def place_order_from_cart(request):
    user = request.user

    try:
        # Fetch the user's cart
        cart = Cart.objects.get(user=user)
        cart_items = cart.items.all()

        if not cart_items:
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Create the order
            order = Order.objects.create(user=user)

            # Move items from the cart to the order
            for item in cart_items:
                product = item.product
                if product.stock < item.quantity:
                    return Response(
                        {"error": f"Not enough stock for {product.name}."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                product.stock -= item.quantity
                product.save()

                # Create the order item
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price,
                )

            # Clear the cart
            cart.items.all().delete()

            return Response({"message": "Order placed successfully.", "order_id": order.id}, status=status.HTTP_201_CREATED)

    except Cart.DoesNotExist:
        return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)
