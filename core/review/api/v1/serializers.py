from rest_framework import serializers
from review.models import Review

class ReviewSerializers(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model= Review
        fields=[
             "id",
            "user",
            "product",
            "rating",
            "comment",
            "is_active",
            "created_date",
            "updated_date",
        ]
        read_only_fields = ["id", "user", "is_active", "created_date", "updated_date"]

class CreateReviewSerializers(serializers.ModelSerializer):
        class Meta:
            model = Review
            fields = ["product", "rating", "comment"]