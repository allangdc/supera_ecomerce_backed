from rest_framework import viewsets
from choice_items.models import ChoiceItems
from choice_items.serializer import ChoiceItemsSerializer


class ChoiceItemsViewSet(viewsets.ModelViewSet):
    queryset = ChoiceItems.objects.all()
    serializer_class = ChoiceItemsSerializer
