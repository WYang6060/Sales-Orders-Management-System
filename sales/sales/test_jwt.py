from django.test import TestCase
from django.contrib.auth.models import User
import json


test_users = [
    {'username': 'username1', 'password': 'password1'},
    {'username': 'username2', 'password': 'password2'},
]

class LoginTest(TestCase):
    def setUp(self):
        for user in test_users:
            new_user = User.objects.create(username=user['username'])
            new_user.set_password(user['password'])
            new_user.save()

    def test_login(self):
        test_user = test_users[0]
        res = self.client.post('/api/token/',
                               data=json.dumps({
                                   'username': test_user['username'],
                                   'password': test_user['password'],
                               }),
                               content_type='application/json',
        )
        result = json.loads(res.content)
        self.assertTrue('access' in result)