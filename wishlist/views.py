from rest_framework import viewsets, mixins
from wishlist.models import Status, Wishlist
from wishlist.serializer import StatusSerializer, WishlistSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response


class StatusViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Status.objects.all()
    serializer_class = StatusSerializer


class WishlistViewset(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        query = qs.filter(id_user=self.request.user)
        return query

    def perform_create(self, serializer):
        st = Status.objects.filter(name="Pending").first()
        ret = Wishlist.objects.filter(
            Q(status=st) & Q(id_user=self.request.user))
        if not ret:
            serializer.save(id_user=self.request.user)
        else:
            raise ValidationError(
                "Cannot create a wishlist if there is a pending list.")

    def perform_update(self, serializer):
        finish_status = Status.objects.get(name="Finished")
        purchase_date = serializer.validated_data.get("purchase_date")
        status = serializer.validated_data.get("status")

        if purchase_date is not None or status != finish_status:
            return super().perform_update(serializer)
        raise ValidationError(
            "It is not possible to finalize a wish list without a purchase date.")

    # Route to bring up the wishlist that is pending.
    @action(detail=False,  methods=['get'])
    def pending(self, request):
        st = Status.objects.get(name="Pending")
        try:
            wishlist_pending = self.get_queryset().get(status=st)
            serializer = self.get_serializer(wishlist_pending, many=False)
            return Response(serializer.data)
        except:
            raise NotFound()
