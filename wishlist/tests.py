from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from wishlist.models import Wishlist, Status

STATUS_PENDING = "Pending"
STATUS_FINISHED = "Finished"


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

    def setUp(self):
        usr1 = User.objects.create_user(username='user1', password='user1')
        usr2 = User.objects.create_user(username='user2', password='user2')
        st = Status.objects.get(name=STATUS_FINISHED)
        Wishlist.objects.create(
            id_user=usr1, shipping_price=0, purchase_date=None, status=st)
        Wishlist.objects.create(
            id_user=usr1, shipping_price=0, purchase_date=None, status=st)
        Wishlist.objects.create(
            id_user=usr2, shipping_price=0, purchase_date=None, status=st)

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

    def test_create_wishlist_not_logged(self):
        # User not logged cannot write to table.
        st = Status.objects.get(name=STATUS_PENDING)
        res = self.client.post(self.url_wishlist, {
            "purchase_date": None,
            "status": st.id
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_wishlist_logged_user1(self):
        # User logged can write and check if the id_user field has been linked correctly.
        usr = self.loginUser1()
        st = Status.objects.get(name=STATUS_PENDING)
        res = self.client.post(self.url_wishlist, {
            "purchase_date": None,
            "status": st.id
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.client.logout()

        # Checks if it was created with the correct id_user
        wl = Wishlist.objects.filter(id=res.data["id"]).first()
        self.assertEqual(wl.id_user, usr)

    def test_create_wishlist_logged_user2(self):
        # User logged can write and check if the id_user field has been linked correctly.
        usr = self.loginUser2()
        st = Status.objects.get(name=STATUS_PENDING)
        res = self.client.post(self.url_wishlist, {
            "purchase_date": None,
            "status": st.id
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.client.logout()

        # Checks if it was created with the correct id_user
        wl = Wishlist.objects.filter(id=res.data["id"]).first()
        self.assertEqual(wl.id_user, usr)

    def test_create_wishlist_shipping_must_be_0(self):
        usr = self.loginUser1()
        st = Status.objects.get(name=STATUS_PENDING)
        res = self.client.post(self.url_wishlist, {
            "purchase_date": None,
            "status": st.id
        }, format="json")
        self.client.logout()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["shipping_price"], 0)

    def test_error_two_pending_wishlist(self):
        # A wishlist cannot be created if there is already a list with status=pending
        usr = self.loginUser1()
        st = Status.objects.get(name=STATUS_PENDING)
        res = self.client.post(self.url_wishlist, {
            "purchase_date": None,
            "status": st.id
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.client.logout()

        usr = self.loginUser2()
        st = Status.objects.get(name=STATUS_PENDING)
        res = self.client.post(self.url_wishlist, {
            "purchase_date": None,
            "status": st.id
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # User2 already has a pending wishlist.
        res = self.client.post(self.url_wishlist, {
            "purchase_date": None,
            "status": st.id
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.client.logout()

    def test_finish_wishlist_with_purchase_date(self):
        usr = self.loginUser1()
        st = Status.objects.get(name=STATUS_PENDING)
        res = self.client.post(self.url_wishlist, {
            "purchase_date": None,
            "status": st.id
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        newst = Status.objects.get(name=STATUS_FINISHED)
        url_update = "{}{}/".format(self.url_wishlist, res.data["id"])
        newres = self.client.patch(url_update, {
            "purchase_date": "2022-06-05T10:53:15.949197Z",
            "status": newst.id
        }, format="json")
        self.assertEqual(newres.status_code, status.HTTP_200_OK)

        self.client.logout()

    def test_error_finish_wishlist_without_purchase_date(self):
        usr = self.loginUser1()
        st = Status.objects.get(name=STATUS_PENDING)
        res = self.client.post(self.url_wishlist, {
            "purchase_date": None,
            "status": st.id
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        newst = Status.objects.get(name=STATUS_FINISHED)
        url_update = "{}{}/".format(self.url_wishlist, res.data["id"])
        newres = self.client.patch(url_update, {
            "purchase_date": None,
            "status": newst.id
        }, format="json")
        self.assertEqual(newres.status_code, status.HTTP_400_BAD_REQUEST)

        self.client.logout()

    def test_pending_wishlist_route(self):
        url_pending = "{}pending/".format(self.url_wishlist)
        self.loginUser1()
        st = Status.objects.get(name=STATUS_PENDING)
        res = self.client.post(self.url_wishlist, {
            "purchase_date": None,
            "status": st.id
        }, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        res_all = self.client.get(self.url_wishlist, format="json")
        self.assertEqual(res_all.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_all.data), 3)

        res_pending = self.client.get(url_pending, format="json")
        self.assertEqual(res_pending.status_code, status.HTTP_200_OK)
        self.assertEqual(res_pending.data["id"], res.data["id"])

    def test_anyone_pending_wishlist_route(self):
        url_pending = "{}pending/".format(self.url_wishlist)
        self.loginUser1()
        res_pending = self.client.get(url_pending, format="json")
        self.assertEqual(res_pending.status_code, status.HTTP_404_NOT_FOUND)