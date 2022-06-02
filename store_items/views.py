from rest_framework import viewsets
from store_items.models import StoreItems
from store_items.serializer import StoreItemsSerializer


class StoreItemsViewset(viewsets.ModelViewSet):
    queryset = StoreItems.objects.all()
    serializer_class = StoreItemsSerializer
