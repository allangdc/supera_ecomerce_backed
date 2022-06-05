from rest_framework import serializers
from wishlist.models import Wishlist, Status


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = "__all__"


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ["id", "shipping_price", "purchase_date",
                  "created_at", "updated_at", "id_user", "status"]
        extra_kwargs = {'id_user': {'read_only': True}}
        
