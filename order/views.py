from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem, Product, Order, OrderItem, Payment
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, PaymentSerializer

from rest_framework.permissions import IsAuthenticated
from server.permissions import IsCustomer

from django.db import transaction
import redis
from django.conf import settings

# Connect to Redis
redis_client = redis.StrictRedis.from_url(settings.CACHES['default']['LOCATION'])


# Ensure the user has a cart, if not, create one
@api_view(['GET'])
@permission_classes([IsCustomer])
def get_or_create_cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    
    # Serialize the cart and return it
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsCustomer])
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
@permission_classes([IsCustomer])
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
@permission_classes([IsCustomer])
def delete_from_cart(request):
    user = request.user
    product_id = request.data.get('product_id')
    quantity = request.data.get('quantity', 1)

    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return Response({"detail": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # Get the product object
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
    except CartItem.DoesNotExist:
        return Response({"detail": "CartItem not found"})
    
    if cart_item.quantity<quantity:
        return Response({"detail": f"Cannot delete {quantity} from {cart_item.quantity} items."})
    
    cart_item.quantity -= quantity
    cart_item.save()
    return Response({
        "message": "Item deleted from cart",
        "cart_item": CartItemSerializer(cart_item).data
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsCustomer])
def place_order_from_cart(request):
    user = request.user
    cart_key = f"cart_lock:{user.id}"  # Redis key for locking the user's cart
    with redis_client.lock(cart_key, timeout=10):  # 10-second lock
    
        try:
            # Fetch the user's cart
            cart = Cart.objects.get(user=user)
            cart_items = cart.items.all()

            if not cart_items:
                return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                # Create the order
                cart = Cart.objects.get(user=user)
                cart_items = cart.items.all()
                for item in cart_items:
                    product = item.product
                    if product.stock < item.quantity:
                        raise ValueError(f"Not enough stock for {product.name}.")
                    
                order = Order.objects.create(user=user)
                
                payment,created = Payment.objects.get_or_create(order=order,
                                                                payment_method="Credit Card",
                                                                amount=1,  # Assume you calculate the total order amount
                                                                transaction_id="unique_txn_id_12345",  # Generated by your payment processor
                                                                status="PENDING")
                

                return Response({"message": "Please make payment to proceed", "order_id": order.id}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            # Handle stock errors and ensure rollback
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({"error": "Cart not found."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsCustomer])
def view_orders(request,user_id=None):
    if not user_id:
        orders = Order.objects.prefetch_related("items").select_related('user')
    else:
        orders = Order.objects.filter(user_id = user_id)
    # Serialize the data
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
def update_payment_status(request,payment_id=None):
    if not payment_id:
        return Response({"error": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)
    
    payment = Payment.objects.get(id=payment_id)
    serializer = PaymentSerializer(payment, data = request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        if request.data['status']=='SUCCESS':
            user = request.user 
            cart = Cart.objects.get(user=user)
            cart_items = cart.items.all()
            for item in cart_items:
                product = item.product
                if product.stock < item.quantity:
                    raise ValueError(f"Not enough stock for {product.name}.")

                product.stock -= item.quantity
                product.save()

                # Clear the cart
                
            
            order = payment.order
            order.status= 'COMPLETED'
            order.save() 
            for item in cart_items:
                orderItem = OrderItem.objects.create(order=order,
                                                        product=item.product,
                                                        quantity=item.quantity,  # Specify the quantity
                                                        price=product.price  # Specify the price
                                                        )
            
            cart.items.all().delete()


        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
