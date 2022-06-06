from django.db import models
from django.contrib.auth.models import User


class Status(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Wishlist(models.Model):
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    shipping_price = models.FloatField(default=0.0)
    total_price = models.FloatField(default=0.0)
    total_items = models.IntegerField(default=0)
    purchase_date = models.DateTimeField(null=True, blank=True, default=None)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return "user: {} - Wishlist: {} - status: {}".format(self.id_user, 
                                                            self.id,
                                                            self.status)

