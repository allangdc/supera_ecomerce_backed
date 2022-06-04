from rest_framework import viewsets, mixins
from wishlist.models import Status, Wishlist
from wishlist.serializer import StatusSerializer, WishlistSerializer
from rest_framework.permissions import IsAuthenticated


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
        serializer.save(id_user=self.request.user)
