from http.client import NOT_FOUND
from rest_framework.viewsets import ModelViewSet, mixins, GenericViewSet
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from user_info.serializer import UserSerializer
from rest_framework.exceptions import NotFound


class UsersViewSet(mixins.ListModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        query = qs.filter(id=self.request.user.id)
        return query
