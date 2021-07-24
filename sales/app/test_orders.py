from unittest import result
from django.test import TestCase
from django.contrib.auth.models import User
import json

test_user = {
    'username': 'testuser', 
    'password': 'testpwd'
}
test_data = {
    'date': '2021-07-19',
    'item': 'Pizza',
    'price': 30,
    'quantity': 10
}


class OrdersTest(TestCase):
    def __init__(self, methodName: str) -> None:
        super().__init__(methodName=methodName)

        self.user = test_user
        self.data = test_data

    def setUp(self):
        user = User.objects.create(username=self.user['username'])
        user.set_password(self.user['password'])
        user.save()


    def get_token(self):
        res = self.client.post(
            '/api/token/',
            data=json.dumps({'username': self.user['username'], 'password': self.user['password']}),
            content_type='application/json',
        )
        result = json.loads(res.content)
        self.assertTrue('access' in result)

        return result['access']


    #########################   FORBIDDEN & OK   ##########################

    def test_add_orders_forbidden(self):
        # without token
        res = self.client.post(
            '/api/orders/',
            data=json.dumps(self.data),
            content_type='application/json',
        )
        self.assertEquals(res.status_code, 401)

        # with wrong token
        res = self.client.post(
            '/api/orders/',
            data=json.dumps(self.data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer Wront Token',
        )
        self.assertEquals(res.status_code, 401)


    def test_add_orders_ok(self):
        token = self.get_token()
        res = self.client.post(
            '/api/orders/',
            data=json.dumps(self.data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(res.status_code, 201)

        result = json.loads(res.content)['data']
        self.assertEquals(result['date'], self.data['date'])
        self.assertEquals(result['item'], self.data['item'])
        self.assertEquals(result['price'], self.data['price'])
        self.assertEquals(result['quantity'], self.data['quantity'])


    def test_add_orders_wrong_data(self):
        token = self.get_token()

        # without item
        res = self.client.post(
            '/api/orders/',
            data=json.dumps({**self.data, 'item': ''}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(res.status_code, 400)

        # wrong price: price >= 0
        res = self.client.post(
            '/api/orders/',
            data=json.dumps({**self.data, 'price': -1}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(res.status_code, 400)

        # wrong quantity: quantity >= 0
        res = self.client.post(
            '/api/orders/',
            data=json.dumps({**self.data, 'quantity': -1}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(res.status_code, 400)


    def test_add_orders_calculate(self):
        token = self.get_token()
        res = self.client.post(
            '/api/orders/',
            data=json.dumps({**self.data, 'amount': 1000}),     # 'amount' should be ignored
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(res.status_code, 201)

        result = json.loads(res.content)['data']
        self.assertEquals(result['amount'], self.data['price'] * self.data['quantity'])     # 'amount' should be calcaulted


    ########################   GET   ##########################

    def test_get_records(self):
        token = self.get_token()

        # get id of first data
        res = self.client.post(
            '/api/orders/',
            data=json.dumps(self.data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(res.status_code, 201)
        id1 = json.loads(res.content)['data']['id']

        # get id of second data
        res = self.client.post(
            '/api/orders/',
            data=json.dumps({**self.data, 'price': 1, 'quantity': 20}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(res.status_code, 201)
        id2 = json.loads(res.content)['data']['id']

        # get all data
        res = self.client.get(
            '/api/orders/',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)['data']

        # check 2 data (first data and second one)
        self.assertEquals(len(result), 2)
        self.assertTrue(result[0]['id'] == id1 or result[1]['id'] == id1)
        self.assertTrue(result[0]['id'] == id2 or result[1]['id'] == id2)

        # get first data
        # check if it is identical to the original data
        res = self.client.get(
            f'/api/orders/{id1}/',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)['data']
        self.assertEquals(result['date'], self.data['date'])
        self.assertEquals(result['item'], self.data['item'])
        self.assertEquals(result['price'], self.data['price'])
        self.assertEquals(result['quantity'], self.data['quantity'])
        self.assertEquals(result['amount'], self.data['price'] * self.data['quantity'])


    ##########################   PUT & DELETE   ##########################

    def test_put_delete_records(self):
        token = self.get_token()

        # get id
        res = self.client.post(
            '/api/orders/',
            data=json.dumps(self.data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(res.status_code, 201)
        id = json.loads(res.content)['data']['id']

        # new data for put
        new_data = {
            'date': '2021-07-20',
            'item': 'Hamburger',
            'price': 2,
            'quantity': 100
        }

        # update {id}th data
        res = self.client.put(
            f'/api/orders/{id}/',
            data=json.dumps(new_data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)['data']
        self.assertEquals(result['date'], new_data['date'])

        # get {id}th data
        res = self.client.get(
            f'/api/orders/{id}/',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )

        self.assertEquals(res.status_code, 200)
        result = json.loads(res.content)['data']
        self.assertEquals(result['date'], new_data['date'])
        self.assertEquals(result['item'], new_data['item'])
        self.assertEquals(result['price'], new_data['price'])
        self.assertEquals(result['quantity'], new_data['quantity'])
        self.assertEquals(result['amount'], new_data['price'] * new_data['quantity'])

        # delete {id}th data
        res = self.client.delete(
            f'/api/orders/{id}/',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(res.status_code, 410)     # gone

        # get {id}th data
        res = self.client.get(
            f'/api/orders/{id}/',
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        self.assertEquals(res.status_code, 404)     # not found
