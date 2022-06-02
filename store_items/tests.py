from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from store_items.models import StoreItems
from django.conf import settings
import os


class StoreItemsApiTest(APITestCase):
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
        b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
        b'\x02\x4c\x01\x00\x3b'
    )
    gifname = "file_test"
    url = '/api/v1/store-items/'

    def setUp(self):
        image = SimpleUploadedFile(
            "{0}.gif".format(self.gifname), self.small_gif, content_type="image/gif")
        response = self.client.post(self.url, {
            "name": "TestStore",
            "price": 125.25,
            "score": 200,
            "image": image
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def tearDown(self) -> None:
        # Getting the ID
        item = StoreItems.objects.get(name="TestStore")
        url_delete = "{}{}/".format(self.url, item.id)

        # Deleting the temp record
        response = self.client.delete(url_delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_allitems(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "TestStore")
        self.assertTrue(
            str(response.data[0]["image"]).__contains__(self.gifname))

    def test_get_id_item(self):
        # getting the id
        item = StoreItems.objects.get(name="TestStore")
        get_url_item = "{}{}/".format(self.url, item.id)

        response = self.client.get(get_url_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "TestStore")
        self.assertTrue(str(response.data["image"]).__contains__(self.gifname))

    def test_storage_image(self):
        # Creating a new Item
        image = SimpleUploadedFile(
            "{0}.gif".format("NewGifFile"), self.small_gif, content_type="image/gif")
        response = self.client.post(self.url, {
            "name": "NewNameFile",
            "price": 125.25,
            "score": 200,
            "image": image
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Checking in the database the name of the file.
        item = StoreItems.objects.get(name="NewNameFile")
        image_dir = os.path.join(settings.MEDIA_ROOT, item.image.name)

        # Check if file exists
        self.assertTrue(os.path.exists(image_dir))

        # Try to delete the new register
        url_delete = "{}{}/".format(self.url, item.id)
        response = self.client.delete(url_delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Check if file doesn't exist
        self.assertFalse(os.path.exists(image_dir))
