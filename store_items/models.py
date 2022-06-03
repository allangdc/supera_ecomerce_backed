from django.db import models

from django.dispatch import receiver
import os


class StoreItems(models.Model):
    name = models.CharField(max_length=250)
    price = models.FloatField()
    score = models.IntegerField()
    image = models.ImageField(upload_to="games_cover")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


@receiver(models.signals.post_delete, sender=StoreItems)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Files` object is deleted.
    """
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)


@receiver(models.signals.pre_save, sender=StoreItems)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `Files` object is updated
    with new file.
    """
    if not instance.pk:
        return False
    
    try:
        old_image = StoreItems.objects.get(pk=instance.pk).image
    except StoreItems.DoesNotExist:
        return False

    new_image = instance.image
    if not old_image == new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)
