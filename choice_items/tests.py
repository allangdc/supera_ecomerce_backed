from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from rest_framework import status
from choice_items.models import ChoiceItems
from store_items.models import StoreItems
from wishlist.models import Wishlist, Status

STATUS_PENDING = "Pending"
STATUS_FINISHED = "Finished"


class ChoiceItemsApiTest(APITestCase):
    fixtures = ["wishlist_status.json"]
    url_choice_items = '/api/v1/choice-items/'
    small_gif = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
        b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
        b'\x02\x4c\x01\x00\x3b'
    )

    def setUp(self) -> None:
        User.objects.create_user(username='user1', password='user1')
        User.objects.create_user(username='user2', password='user2')
        self.create_store_item("item_a", 83.60)
        self.create_store_item("item_b", 90.45)
        self.create_store_item("item_c", 75.95)

    def tearDown(self) -> None:
        items = StoreItems.objects.all()
        items.delete()

    def loginUser1(self):
        self.client.login(username="user1", password="user1")
        return User.objects.filter(username="user1").first()

    def loginUser2(self):
        self.client.login(username="user2", password="user2")
        return User.objects.filter(username="user2").first()

    def create_wishlist(self, username, status):
        usr = User.objects.get(username=username)
        st = Status.objects.get(name=status)
        return Wishlist.objects.create(id_user=usr, shipping_price=0,
                                       purchase_date=None, status=st)

    def create_store_item(self, itemname, price=83.60, score=200):
        img = SimpleUploadedFile("{0}.gif".format(
            itemname), self.small_gif, content_type="image/gif")
        return StoreItems.objects.create(name=itemname, price=price, 
                                        score=score, image=img)

    def create_choice_item(self, username, itemname):
        wishlist = self.create_wishlist(username, STATUS_PENDING)
        store_item = StoreItems.objects.get(name=itemname)
        choice_item = ChoiceItems.objects.create(
            id_item=store_item, id_wishlist=wishlist)
        return choice_item, store_item, wishlist

    def test_get_choice_item_user_logged(self):
        citem, sitem, wsl = self.create_choice_item("user1", "item_b")
        self.loginUser1()
        res = self.client.get(self.url_choice_items, format="json")
        self.client.logout()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id_item"], sitem.id)
        self.assertEqual(res.data[0]["id_wishlist"], wsl.id)

    def test_error_get_choice_item_not_logged(self):
        citem, sitem, wsl = self.create_choice_item("user1", "item_b")
        res = self.client.get(self.url_choice_items, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_choice_item_not_show_other_users(self):
        self.create_choice_item("user2", "item_b")
        self.create_choice_item("user2", "item_c")
        citem, sitem, wsl = self.create_choice_item("user1", "item_a")
        self.loginUser1()
        res = self.client.get(self.url_choice_items, format="json")
        self.client.logout()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["id_item"], sitem.id)
        self.assertEqual(res.data[0]["id_wishlist"], wsl.id)

    def test_create_choice_item(self):
        wsl = self.create_wishlist("user1", STATUS_PENDING)
        sitem = StoreItems.objects.get(name="item_a")
        self.loginUser1()
        res = self.client.post(self.url_choice_items, {
            "id_item": sitem.id,
            "id_wishlist": wsl.id
        }, format="json")
        self.client.logout()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_error_create_choice_item_finished_wishlist(self):
        wsl = self.create_wishlist("user1", STATUS_FINISHED)
        sitem = StoreItems.objects.get(name="item_a")
        self.loginUser1()
        res = self.client.post(self.url_choice_items, {
            "id_item": sitem.id,
            "id_wishlist": wsl.id
        }, format="json")
        self.client.logout()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_create_choice_item_different_user(self):
        wsl = self.create_wishlist("user1", STATUS_PENDING)
        sitem = StoreItems.objects.get(name="item_a")
        self.loginUser2()
        res = self.client.post(self.url_choice_items, {
            "id_item": sitem.id,
            "id_wishlist": wsl.id
        }, format="json")
        self.client.logout()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def get_wishlist_shipping(self, wishlist_id):
        ck_wishlist = Wishlist.objects.get(id=wishlist_id)
        return ck_wishlist.shipping_price

    def get_wishlist_total_items(self, wishlist_id):
        ck_wishlist = Wishlist.objects.get(id=wishlist_id)
        return ck_wishlist.total_items

    def get_wishlist_total_price(self, wishlist_id):
        ck_wishlist = Wishlist.objects.get(id=wishlist_id)
        return ck_wishlist.total_price

    def test_shipping(self):
        # pre-adding item from another user
        self.create_choice_item("user2", "item_b")

        # Now adding user1 items
        wsl = self.create_wishlist("user1", STATUS_PENDING)
        sitem_a = StoreItems.objects.get(name="item_a")  # price=83.60
        sitem_b = StoreItems.objects.get(name="item_b")  # price=90.45
        sitem_c = StoreItems.objects.get(name="item_c")  # price=75.95
        self.loginUser1()
        # 1st
        res1 = self.client.post(self.url_choice_items, {
            "id_item": sitem_a.id, "id_wishlist": wsl.id}, format="json")
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.get_wishlist_total_items(wsl.id), 1)
        self.assertEqual(self.get_wishlist_total_price(wsl.id), 83.60)
        self.assertEqual(self.get_wishlist_shipping(wsl.id), 10)  # Total=83.60

        # 2nd
        res2 = self.client.post(self.url_choice_items, {
            "id_item": sitem_b.id, "id_wishlist": wsl.id}, format="json")
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.get_wishlist_total_items(wsl.id), 2)
        self.assertEqual(self.get_wishlist_total_price(wsl.id), 174.05)
        self.assertEqual(self.get_wishlist_shipping(wsl.id), 20)  # Total=174,05

        # 3nd
        res3 = self.client.post(self.url_choice_items, {
            "id_item": sitem_c.id, "id_wishlist": wsl.id}, format="json")
        self.assertEqual(res3.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.get_wishlist_total_items(wsl.id), 3)
        self.assertEqual(self.get_wishlist_total_price(wsl.id), 250)
        self.assertEqual(self.get_wishlist_shipping(wsl.id), 0)  # Total=250

        # 4nd
        res3 = self.client.post(self.url_choice_items, {
            "id_item": sitem_c.id, "id_wishlist": wsl.id}, format="json")
        self.assertEqual(res3.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.get_wishlist_total_items(wsl.id), 4)
        self.assertEqual(self.get_wishlist_total_price(wsl.id), 325.95)
        self.assertEqual(self.get_wishlist_shipping(wsl.id), 0)  # Total=325.95

        # Removing items to test
        url_delete_item = "{}{}/".format(self.url_choice_items,
                                         res3.data["id"])
        res = self.client.delete(url_delete_item)   # removing 90.45
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.get_wishlist_total_items(wsl.id), 3)
        self.assertEqual(self.get_wishlist_total_price(wsl.id), 250)
        self.assertEqual(self.get_wishlist_shipping(wsl.id), 0)  # Total=250

        url_delete_item = "{}{}/".format(self.url_choice_items,
                                         res2.data["id"])
        res = self.client.delete(url_delete_item)   # removing 90.45
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.get_wishlist_total_items(wsl.id), 2)
        self.assertEqual(self.get_wishlist_total_price(wsl.id), 159.55)
        self.assertEqual(self.get_wishlist_shipping(wsl.id), 20)  # Total=159.55

        url_delete_item = "{}{}/".format(self.url_choice_items,
                                         res1.data["id"])
        res = self.client.delete(url_delete_item) # removing 83.60
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.get_wishlist_total_items(wsl.id), 1)
        self.assertEqual(self.get_wishlist_total_price(wsl.id), 75.95)
        self.assertEqual(self.get_wishlist_shipping(wsl.id), 10)  # Total=75.95

        self.client.logout()
