from django.db import models

class StoreItems(models.Model):
    name = models.CharField(max_length=250)
    price = models.FloatField()
    score = models.IntegerField()
    image = models.ImageField(upload_to="games_cover")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name