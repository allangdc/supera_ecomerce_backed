from rest_framework import serializers
from wishlist.models import Wishlist, Status


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = "__all__"


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ["id", "shipping_price", "total_items", "total_price", "purchase_date",
                  "created_at", "updated_at", "id_user", "status"]
        extra_kwargs = {'id_user': {'read_only': True},
                        'shipping_price': {'read_only': True},
                        'total_items': {'read_only': True},
                        'total_price': {'read_only': True}}
