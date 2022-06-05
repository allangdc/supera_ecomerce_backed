from rest_framework.routers import SimpleRouter
from wishlist.views import StatusViewset, WishlistViewset

status_router = SimpleRouter()
status_router.register("", StatusViewset)

wishlist_router = SimpleRouter()
wishlist_router.register("", WishlistViewset)