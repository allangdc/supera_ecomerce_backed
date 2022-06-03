from urllib import response
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from store_items.models import StoreItems
from django.contrib.auth.models import User
from django.conf import settings
import os


class StoreItemsApiTest(APITestCase):
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
        b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
        b'\x02\x4c\x01\x00\x3b'
    )
    generic_item = "TestStoreItem"
    url = '/api/v1/store-items/'

    @classmethod
    def setUpClass(cls):
        # Creating test users.
        user = User.objects.create_superuser(
            username='admin', password='admin')
        user = User.objects.create_user(username='guest', password='guest')
        super(StoreItemsApiTest, cls).setUpClass()

    def setUp(self):
        img = SimpleUploadedFile("{0}.gif".format(
            self.generic_item), self.small_gif, content_type="image/gif")
        item = StoreItems.objects.create(
            name=self.generic_item, price=125.25, score=200, image=img)

    def tearDown(self) -> None:
        item = StoreItems.objects.all()
        item.delete()

    def loginRegularUser(self):
        ret = self.client.login(username="regular", password="regular")

    def loginAdminUser(self):
        ret = self.client.login(username="admin", password="admin")

    def test_add_item_as_not_logged(self):
        # Trying to add an item with no user logged. (MUST NOT HAVE PERMISSION)
        img = SimpleUploadedFile(
            "{0}.gif".format("TestItemImage"), self.small_gif, content_type="image/gif")
        response = self.client.post(self.url, {
            "name": "TestItem",
            "price": 125.25,
            "score": 200,
            "image": img
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_item_as_regular_user(self):
        # Trying to add an item as a regular user. (MUST NOT HAVE PERMISSION)
        self.loginRegularUser()
        img2 = SimpleUploadedFile(
            "{0}.gif".format("TestItemImage"), self.small_gif, content_type="image/gif")
        response = self.client.post(self.url, {
            "name": "TestItem",
            "price": 125.25,
            "score": 200,
            "image": img2
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def test_add_item_as_admin_user(self):
        # Trying to add an item as admin. (MUST HAVE PERMISSION)
        self.loginAdminUser()
        img3 = SimpleUploadedFile(
            "{0}.gif".format("TestItemImage"), self.small_gif, content_type="image/gif")
        response = self.client.post(self.url, {
            "name": "TestItem",
            "price": 150.25,
            "score": 200,
            "image": img3
        }, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.logout()

        item = StoreItems.objects.get(name="TestItem")

        # Checking if the image has been added to the "media/" folder
        image_dir = os.path.join(settings.MEDIA_ROOT, item.image.name)
        self.assertTrue(os.path.exists(image_dir))


    def create_delete_item(self):
        # Creating an item to be removed
        img = SimpleUploadedFile("{0}.gif".format(
            "TestRemoveImage"), self.small_gif, content_type="image/gif")
        item = StoreItems.objects.create(
            name="TestRemoveItem", price=125.25, score=200, image=img)

        image_dir = os.path.join(settings.MEDIA_ROOT, item.image.name)
        url_delete = "{}{}/".format(self.url, item.id)
    
        return image_dir, url_delete

    def test_delete_item_as_not_logged(self):
        # Creating an item to be removed
        image_dir, url_delete = self.create_delete_item()

        # Trying to delete an item with no user logged in. (MUST NOT HAVE PERMISSION)
        response = self.client.delete(url_delete)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # image must not have been removed
        self.assertTrue(os.path.exists(image_dir))

    def test_delete_item_as_regular_user(self):
        # Creating an item to be removed
        image_dir, url_delete = self.create_delete_item()

        # Trying to delete an item as a regular user. (MUST NOT HAVE PERMISSION)
        self.loginRegularUser()
        response = self.client.delete(url_delete)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()
        # image must not have been removed
        self.assertTrue(os.path.exists(image_dir))

    def test_delete_item_as_admin_user(self):
        # Creating an item to be removed
        image_dir, url_delete = self.create_delete_item()

        # Trying to add an item as admin. (MUST HAVE PERMISSION)
        self.loginAdminUser()
        response = self.client.delete(url_delete)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.client.logout()
        # image must have been removed
        self.assertFalse(os.path.exists(image_dir))

    def create_update_item(self):
        # Creating an item to be updated
        img = SimpleUploadedFile("{0}.gif".format(
            "TestUpdateImage"), self.small_gif, content_type="image/gif")
        item = StoreItems.objects.create(
            name="TestUpdateItem", price=125.25, score=200, image=img)

        old_image_dir = os.path.join(settings.MEDIA_ROOT, item.image.name)
        url_update = "{}{}/".format(self.url, item.id)
        return old_image_dir, url_update

    def test_updating_item_as_not_logged(self):
        # Creating an item to be updated
        old_image_dir, url_update = self.create_update_item()

        # Updating as user not logged (MUST NOT HAVE PERMISSION)
        newimg = SimpleUploadedFile("{0}.gif".format(
            "TestUpdateNewImage"), self.small_gif, content_type="image/gif")
        response = self.client.patch(url_update, {
            "name": "TestUpdateNewName",
            "image": newimg,
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_updating_item_as_regular_user(self):
        # Creating an item to be updated
        old_image_dir, url_update = self.create_update_item()

        # Updating as regular user (MUST NOT HAVE PERMISSION)
        self.loginRegularUser()
        newimg = SimpleUploadedFile("{0}.gif".format(
            "TestUpdateNewImage"), self.small_gif, content_type="image/gif")
        response = self.client.patch(url_update, {
            "name": "TestUpdateNewName",
            "image": newimg,
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.client.logout()

    def test_updating_item_as_admin_user(self):
        # Creating an item to be updated
        old_image_dir, url_update = self.create_update_item()

        # Updating as admin
        self.loginAdminUser()
        newimg = SimpleUploadedFile("{0}.gif".format(
            "TestUpdateNewImage"), self.small_gif, content_type="image/gif")
        response = self.client.patch(url_update, {
            "name": "TestUpdateNewName",
            "image": newimg,
        }, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # old image must be removed
        self.assertFalse(os.path.exists(old_image_dir))
        self.client.logout()

    def test_get_allitems_as_not_logged(self):
        # Everyone must have read access. There should be only the generic item.

        # User not logged.
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], self.generic_item)
        self.assertTrue(
            str(response.data[0]["image"]).__contains__(self.generic_item))

    def test_get_allitems_as_regular_user(self):
        # Everyone must have read access. There should be only the generic item.

        # Logged as regular user
        self.loginRegularUser()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], self.generic_item)
        self.assertTrue(
            str(response.data[0]["image"]).__contains__(self.generic_item))
        self.client.logout()

    def test_get_allitems_as_admin_user(self):
        # Everyone must have read access. There should be only the generic item.

        # Logged as admin
        self.loginAdminUser()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["name"], self.generic_item)
        self.assertTrue(
            str(response.data[0]["image"]).__contains__(self.generic_item))
        self.client.logout()

    def test_get_id_item_as_not_logged(self):
        # Everyone must have read access. There should be only the generic item.
        item = StoreItems.objects.get(name=self.generic_item)
        get_url_item = "{}{}/".format(self.url, item.id)

        # User not logged.
        response = self.client.get(get_url_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.generic_item)
        self.assertTrue(
            str(response.data["image"]).__contains__(self.generic_item))

    def test_get_id_item_as_regular_user(self):
        # Everyone must have read access. There should be only the generic item.
        item = StoreItems.objects.get(name=self.generic_item)
        get_url_item = "{}{}/".format(self.url, item.id)

        # Logged as regular user
        self.loginRegularUser()
        response = self.client.get(get_url_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.generic_item)
        self.assertTrue(
            str(response.data["image"]).__contains__(self.generic_item))
        self.client.logout()

    def test_get_id_item_as_admin_user(self):
        # Everyone must have read access. There should be only the generic item.
        item = StoreItems.objects.get(name=self.generic_item)
        get_url_item = "{}{}/".format(self.url, item.id)

        # Logged as admin
        self.loginAdminUser()
        response = self.client.get(get_url_item, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.generic_item)
        self.assertTrue(
            str(response.data["image"]).__contains__(self.generic_item))
        self.client.logout()
