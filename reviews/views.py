from rest_framework import generics, permissions
from .models import Review
from .serializers import ReviewSerializer
from productapp.models import Product
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects.filter(product_id=product_id)
    
    def create(self, request, *args, **kwargs):
        product_id = self.kwargs['product_id']
        user = self.request.user
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"message": "Product not found."}, status=status.HTTP_404_NOT_FOUND)


        # Get the data from the serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Check if a review already exists for this product and user
        review, created = Review.objects.update_or_create(
            product_id=product_id,
            user=user,
            defaults={
                'rating': serializer.validated_data['rating'],
                'comment': serializer.validated_data['comment']
            }
        )

        # Construct the message based on whether the review was created or updated
        if created:
            message = "Review created successfully."
            status_code = status.HTTP_201_CREATED
        else:
            message = "Review updated successfully."
            status_code = status.HTTP_200_OK

        # Return the appropriate response
        return Response({
            "message": message,
            "review": ReviewSerializer(review).data
        }, status=status_code)
    
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)