from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from wishlist.models import Wishlist, Status


class StatusApiTest(APITestCase):
    fixtures = ["wishlist_status.json"]
    url_status = '/api/v1/wishlist/status/'

    @classmethod
    def setUpClass(cls):
        # Creating test users.
        user = User.objects.create_user(
            username='user_test_status', password='user')
        super(StatusApiTest, cls).setUpClass()

    def loginUser1(self):
        self.client.login(username="user_test_status", password="user")

    def test_check_status_not_logged(self):
        # User not logged in should not have any access to the Status table.
        res = self.client.get(self.url_status, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_check_status_logged(self):
        # Logged user can have access to read Status table.
        self.loginUser1()
        res = self.client.get(self.url_status, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # Must have just the two records added in the wishlist_status.json file
        self.assertEqual(len(res.data), 2)
        res = self.client.post(self.url_status, format="json")
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.client.logout()


class WishlistApiTest(APITestCase):
    fixtures = ["wishlist_status.json"]
    url_wishlist = '/api/v1/wishlist/'

    @classmethod
    def setUpClass(cls):
        # Creating test users.
        usera = User.objects.create_user(username='user1', password='user1')
        userb = User.objects.create_user(username='user2', password='user2')
        super(WishlistApiTest, cls).setUpClass()

    def setUp(self):
        st = Status.objects.get(id=1)
        usr1 = User.objects.get(username="user1")
        usr2 = User.objects.get(username="user2")
        Wishlist.objects.create(
            id_user=usr1, shipping_price=50.00, purchase_date=None, status=st)
        Wishlist.objects.create(
            id_user=usr1, shipping_price=100.25, purchase_date=None, status=st)
        Wishlist.objects.create(
            id_user=usr2, shipping_price=200.75, purchase_date=None, status=st)

    def loginUser1(self):
        self.client.login(username="user1", password="user1")
        return User.objects.filter(username="user1").first()

    def loginUser2(self):
        self.client.login(username="user2", password="user2")
        return User.objects.filter(username="user2").first()

    def test_get_wishlist_not_logged(self):
        # User not logged should not have any access to the table.
        res = self.client.get(self.url_wishlist, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_wishlist_logged(self):
        # Logged user can have access to the table.
        self.loginUser1()
        res = self.client.get(self.url_wishlist, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # User1 has 2 register
        self.assertEqual(len(res.data), 2)
        self.client.logout()

        self.loginUser2()
        res = self.client.get(self.url_wishlist, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # User2 has 1 register
        self.assertEqual(len(res.data), 1)
        self.client.logout()

    def test_post_wishlist_not_logged(self):
        # User not logged cannot write to table.
        res = self.client.post(self.url_wishlist, {
            "shipping_price": 500,
            "purchase_date": None,
            "status": 1
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_wishlist_logged_user1(self):
        # User logged can write and check if the id_user field has been linked correctly.
        usr = self.loginUser1()
        res = self.client.post(self.url_wishlist, {
            "shipping_price": 500,
            "purchase_date": None,
            "status": 1
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.client.logout()

        # Checks if it was created with the correct id_user
        wl = Wishlist.objects.filter(id=res.data["id"]).first()
        self.assertEqual(wl.id_user, usr)

    def test_post_wishlist_logged_user2(self):
        # User logged can write and check if the id_user field has been linked correctly.
        usr = self.loginUser2()
        res = self.client.post(self.url_wishlist, {
            "shipping_price": 1500,
            "purchase_date": None,
            "status": 1
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.client.logout()

        # Checks if it was created with the correct id_user
        wl = Wishlist.objects.filter(id=res.data["id"]).first()
        self.assertEqual(wl.id_user, usr)
