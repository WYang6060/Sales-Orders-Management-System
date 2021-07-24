from django.forms.models import model_to_dict
from django.http.response import HttpResponse
from rest_framework.decorators import api_view
from rest_framework import status
from app.models import Order
import json
import datetime
from django.core.exceptions import ObjectDoesNotExist


def serialize_order(order):
    serialized = model_to_dict(order)
    serialized['date'] = str(order.date)
    serialized['price'] = float(order.price)
    serialized['quantity'] = float(order.quantity)
    serialized['amount'] = float(order.amount)

    return serialized


def get_orders_data(request):
    # get all orders data
    orders_all_data = Order.objects.all()
    orders_cnt = orders_all_data.count()

    # get orders data by current page
    page_size = int(request.GET.get('page_size', '10'))
    page_no = int(request.GET.get('page_no', '0'))
    orders_data = list(orders_all_data[page_no * page_size: (page_no + 1) * page_size])
    orders_data = [serialize_order(order) for order in orders_data]

    return HttpResponse(json.dumps({'count': orders_cnt, 'data': orders_data}), status=status.HTTP_200_OK)


def get_order_data(request, order, success_status):
    errs = []
    
    # get item
    item = request.data.get('item', '')
    if item == '':
        errs.append({'item': 'This field is required'})

    # get price
    try:
        price = request.data.get('price', '')
        if price == '':
            errs.append({'price': 'This field is required'})
        else:
            price = int(price)
            if price < 0:
                errs.append({'price': 'Price cannot be negative'})
    except ValueError:
        errs.append({'price': 'Could not parse filed'})

    # get quantity
    try:
        quantity = request.data.get('quantity', '')
        if quantity == '':
            errs.append({'quantity': 'This field is required'})
        else:
            quantity = int(quantity)
            if quantity < 0:
                errs.append({'quantity': 'Quantity cannot be negative'})
    except ValueError:
        errs.append({'quantity': 'Could not parse filed'})

    # get date
    date = request.data.get('date', '')
    if date == '':
        date = datetime.datetime.now()

    # make order
    try:
        if order is None:
            order = Order()
        order.date = date
        order.item = item
        order.price = price
        order.quantity = quantity
        order.amount = price * quantity
        order.save()
    except Exception as e:
        errs.append({'Order': str(e)})

    if len(errs) > 0:
        return HttpResponse(json.dumps({'errors': errs}), status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse(json.dumps({'data': serialize_order(order)}), status=success_status)


@api_view(['GET', 'POST'])
def orders(request):
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({'detail': 'Not authorized'}), status=status.HTTP_401_UNAUTHORIZED)
    elif request.method == 'GET':
        return get_orders_data(request) 
    elif request.method == 'POST':
        return get_order_data(request, None, status.HTTP_201_CREATED)
    else:
        return HttpResponse(json.dumps({'detail': 'Wrong method'}), status=status.HTTP_501_NOT_IMPLEMENTED)
    

@api_view(['GET', 'PUT', 'DELETE'])
def order(request, order_id):
    if request.user.is_anonymous:
        return HttpResponse(json.dumps({'detail': 'Not authorized'}), status=status.HTTP_401_UNAUTHORIZED)
    
    # get order
    try:
        order = Order.objects.get(pk=order_id)
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'detail': 'Not found'}), status=status.HTTP_404_NOT_FOUND)
    
    # response
    if request.method =='GET':
        return HttpResponse(json.dumps({'data': serialize_order(order)}), status=status.HTTP_200_OK)
    elif request.method == 'PUT':
        return get_order_data(request, order, status.HTTP_200_OK)
    elif request.method == 'DELETE':
        order.delete()
        return HttpResponse(json.dumps({'detal': 'deleted'}), status=status.HTTP_410_GONE)
    else:
        return HttpResponse(json.dumps({'detail': 'Wrong Method'}), status=status.HTTP_501_NOT_IMPLEMENTED)
