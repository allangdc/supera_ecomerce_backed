from rest_framework.routers import SimpleRouter
from choice_items.views import ChoiceItemsViewSet

choice_item_routes = SimpleRouter()
choice_item_routes.register("", ChoiceItemsViewSet)
