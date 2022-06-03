from rest_framework import serializers
from store_items.models import StoreItems

class StoreItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreItems
        fields = "__all__"