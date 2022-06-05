from rest_framework import serializers
from choice_items.models import ChoiceItems


class ChoiceItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceItems
        fields = "__all__"
