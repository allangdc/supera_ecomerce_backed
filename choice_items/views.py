from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from choice_items.models import ChoiceItems
from wishlist.models import Wishlist, Status
from choice_items.serializer import ChoiceItemsSerializer
from rest_framework.permissions import IsAuthenticated


class ChoiceItemsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = ChoiceItems.objects.all()
    serializer_class = ChoiceItemsSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        query = qs.filter(id_wishlist__id_user=self.request.user)
        return query

    def perform_create(self, serializer):
        wishlist = serializer.validated_data.get("id_wishlist")
        pending_status = Status.objects.get(name="Pending")
        if wishlist.id_user != self.request.user:
            raise ValidationError(
                "It is not possible to associate an item with another user's wishlist")
        elif wishlist.status != pending_status:
            raise ValidationError(
                "You can only associate an item with a pending wishlist")
        else:
            serializer.save()
