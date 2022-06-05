from django.db import models
from store_items.models import StoreItems
from wishlist.models import Wishlist


class ChoiceItems(models.Model):
    id_item = models.ForeignKey(StoreItems, on_delete=models.CASCADE)
    id_wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return "WISHLIST: [{}], ITEM: [{}]".format(self.id_wishlist, self.id_item)
