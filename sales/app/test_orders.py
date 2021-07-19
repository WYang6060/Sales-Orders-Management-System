import json
from django.test import TestCase
from django.contrib.auth.models import User

test_user = {'username': 'username', 'password': 'password'}

class OrdersTest(TestCase):
    def setUp(self):
        user = User.objects.create(username=test_user['username'])
        user.set_password(test_user['password'])
        user.save()

    def get_token(self):
        res = self.client.post('/api/token/',
                               data=json.dumps({
                                   'username': test_user['username'],
                                   'password': test_user['password'],
                               }),
                               content_type='application/json',
        )
        result = json.loads(res.content)
        self.assertTrue('access' in result)

        return result['access']
