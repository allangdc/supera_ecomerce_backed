from rest_framework.routers import SimpleRouter
from user_info.views import UsersViewSet

user_router = SimpleRouter()
user_router.register("", UsersViewSet)
