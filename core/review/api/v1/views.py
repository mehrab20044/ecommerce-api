from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError

from review.models import Review
from .serializers import CreateReviewSerializers, ReviewSerializers

class ReviewViewset(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(is_active=True).select_related("user", "product")
    
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return CreateReviewSerializers
        return ReviewSerializers
    
    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data["product"]
        
        if Review.objects.filter(user=user,product=product).exists():
            raise ValidationError("You have already reviews this product ")
        serializer.save(user=user)
