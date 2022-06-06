from rest_framework import viewsets
from store_items.models import StoreItems
from store_items.serializer import StoreItemsSerializer
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadonly(BasePermission):
    def __is_admin(self, request):
        return bool(request.user and request.user.is_staff)

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or self.__is_admin(request):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or self.__is_admin(request):
            return True
        return False


class StoreItemsViewset(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadonly]

    queryset = StoreItems.objects.all()
    serializer_class = StoreItemsSerializer
