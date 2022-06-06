from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class UserInfoApiTest(APITestCase):
    url_userinfo = "/api/v1/user-info/"

    def setUp(self) -> None:
        user = User.objects.create_user(username='User1', password='user1')

    def test_userinfo_route(self):
        self.client.login(username="User1", password="user1")
        res = self.client.get(self.url_userinfo, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
