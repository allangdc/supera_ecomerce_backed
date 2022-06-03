from rest_framework.routers import SimpleRouter
from store_items.views import StoreItemsViewset

store_items_router = SimpleRouter()
store_items_router.register("", StoreItemsViewset)