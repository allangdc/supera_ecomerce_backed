# Generated by Django 4.0.4 on 2022-06-05 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wishlist', '0005_wishlist_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlist',
            name='total_items',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='total_price',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='wishlist',
            name='shipping_price',
            field=models.FloatField(default=0),
        ),
    ]
