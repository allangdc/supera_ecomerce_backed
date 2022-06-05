from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from choice_items.models import ChoiceItems
from wishlist.models import Wishlist, Status
from choice_items.serializer import ChoiceItemsSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count


FREE_SHIPPING = 250
ADDITIONAL_SHIPPING = 10


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
            self.recalc_shipping(wishlist)

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        self.recalc_shipping(instance.id_wishlist)

    def recalc_shipping(self, wishlist: Wishlist):
        citem = self.get_queryset().filter(id_wishlist=wishlist)
        result = citem.aggregate(sum=Sum("id_item__price"), total=Count("id"))
        if result["sum"] >= FREE_SHIPPING:
            wishlist.shipping_price = 0
        else:
            wishlist.shipping_price = result["total"] * ADDITIONAL_SHIPPING
        wishlist.save()
