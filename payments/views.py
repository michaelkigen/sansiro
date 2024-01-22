'''from django.shortcuts import render
from django.http import HttpResponse
from django_daraja.mpesa.core import MpesaClient

def index(request):
    cl = MpesaClient()
    # Use a Safaricom phone number that you have access to, for you to be able to view the prompt.
    phone_number = '0797759614'
    amount = 1
    account_reference = 'reference'
    transaction_desc = 'Description'
    callback_url = 'https://darajambili.herokuapp.com/express-payment';
    response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
    return HttpResponse(response)

def stk_push_callback(request):
        data = request.body
        
        return HttpResponse("STK Push in Django")'''
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from .operations import sendSTK, check_payment_status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST,HTTP_404_NOT_FOUND
from rest_framework.response import Response
from .models import PaymentTransaction
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from menu.views import CheckoutView , CartViewSet
from menu.models import Cart , Add_item_to_cart
from django.db.models import Sum
from Profile.models import Profile
from users.models import User
from rest_framework import generics, permissions,status
from .models import PaymentTransaction
from .serializers import PaymentTransactionSerializer
from menu.models import Order
from django.conf import settings
import cloudinary
from cloudinary import uploader
import time
import qrcode
from PIL import Image
from menu.views import CheckoutView
from django.shortcuts import get_object_or_404
from users.emailer import send_center_sms
# Create your views here.

def send_sms(order_id):
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return 'Order not found'

    # Access user details from the order
    user_details = {
        'user_id': order.user.id,
        'user_phone_number': order.user.phone_number,
        'user_first_name': order.user.first_name,
        'user_last_name': order.user.last_name,
    }

    # Access the related food items through the ordered_food reverse relation
    food_items = order.ordered_food.all()

    # Create a list to store food item dictionaries
    food_list = []

    # Loop through food items and add each item's details to the list
    for food_item in food_items:
        food_details = {
            'food_name': food_item.food.food_name,
            'quantity': food_item.quantity,
            'sub_total': food_item.sub_total,
            # Add more food details as needed
        }
        food_list.append(food_details)
    send_center_sms(food_list,user_details)
    # If you want to return or do something with the user details and food items, modify the function accordingly
    return 'SMS sent successfully', user_details, food_list

    
    
    
class Redeem_points(APIView):
    permission_classes = [AllowAny, ]
    def post(self , request):
        user = self.request.user
        profile = Profile.objects.filter(user = user).first()
        points = profile.points
        
        cart = Cart.objects.filter(user=user).first()

        if cart is None:
            return Response({"detail": "Cart not found."}, status=HTTP_404_NOT_FOUND)

        total = sum([item.quantity * item.food.price for item in cart.cart_item.all()])
        print('the total amount is: ', total)
        
        if total == 0 :
            return Response({'error':'please make new order'}) 
    
        if points < 40:
            return Response({'error':'your have not reached withdrawal limit'}) 
        
        shillings = points // 5
            
        if shillings < total:
            return Response({'error':'you have insufficient point to make this order'})
        rem_shillings = int(shillings) - total
        rem_points = rem_shillings * 5
        profile.points = rem_points
        profile.save()
        
        
        checkout_view = CheckoutView()
        order_id = checkout_view.post(request).data.get('order_id')
        
        data = {
            'user' : user,
            'order_id': order_id
        }
        print('THIS IS THE DATA ;',data)

        
        order = Order.objects.get(order_id=order_id)

        order.payment_mode = 'qcoins'
        order.save()
        return Response({'message':'order made'})
    

class PaymentTranactionView(ListCreateAPIView):
    def post(self, request):
        return HttpResponse("OK", status=200)
    

class SubmitView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        data = request.data
        phone_number = data.get('phone_number')
        user = self.request.user
        cart = Cart.objects.filter(user=user).first()

        if cart is None:
            return Response({"detail": "Cart not found."}, status=HTTP_404_NOT_FOUND)

        total = sum([item.quantity * item.food.price for item in cart.cart_item.all()])
        amount = total
        print('the total amount is: ', amount)

        entity_id = 0
        if data.get('entity_id'):
            entity_id = data.get('entity_id')

        paybill_account_number = None
        if data.get('paybill_account_number'):
            paybill_account_number = data.get('paybill_account_number')

        try:
            transaction_id = sendSTK(phone_number, amount, entity_id)
            if transaction_id:
                message = {"status": "ok", "transaction_id": transaction_id}
                return Response(message, status=HTTP_200_OK)
            else:
                # Handle the case where transaction_id is not available
                return Response({"detail": "Transaction ID not available."}, status=HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Error in sendSTK: {str(e)}")
            return Response({"error": "An unexpected error occurred during STK push."}, status=HTTP_400_BAD_REQUEST)

class CheckTransactionOnline(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        trans_id = request.data['transaction_id']
        print("CHECK TRANSACTYION ID ", trans_id)
        transaction = PaymentTransaction.objects.filter(trans_id=trans_id).first()
        print("TRANSACTION TABLE CHECKED")

        try:
            if transaction and transaction.checkout_request_id:
                status_response = check_payment_status(transaction.checkout_request_id)
                print("status response")
                status = status_response.get('status')
                print('STATUS: ', status)
                message = status_response.get('message')
                
                if status == True:
                    user = request.user
                    checkout_view = CheckoutView()
                    order_id = checkout_view.post(request).data.get('order_id')
                    print('ORDER_ID :', order_id)

                    transaction.order_id = order_id
                    transaction.is_finished = True
                    transaction.is_successful = True
                    transaction.user = user
                    transaction.message = message
                    transaction.save()
                    print('SAVED TRANSACTION :', transaction)
                    
                    # GENERATION OF QR CODE
                    
                   
                
                   #handling  points  
                    amount = transaction.amount  
                    profile = Profile.objects.get(user=user) 
                    
               
                    if amount >= 50:
                        profile.points += 5
                        profile.save()
                   #sending email
                    
                    
                 # Pass the transaction as a list
                if status_response["result_code"] == "0":
                    send_sms(order_id)
                    return JsonResponse({"response":status_response,"order_id":order_id}, status=200)
                return JsonResponse(status_response, status=200)
            else:
                return JsonResponse({
                    "message": "Server Error. Transaction not found",
                    "status": False
                }, status=400)
        except PaymentTransaction.DoesNotExist:
            return JsonResponse({
                "message": "Server Error. Transaction not found",
                "status": False
            }, status=400)


class RetryTransaction(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        trans_id = request.data['transaction_id']
        try:
            transaction = PaymentTransaction.objects.filter(id=trans_id).get()
            if transaction and transaction.is_successful:
                return JsonResponse({
                    "message": "ok",
                    "finished": transaction.is_finished,
                    "successful": transaction.is_successful
                },
                    status=200)
            else:
                response = sendSTK(
                    phone_number=transaction.phone_number,
                    amount=transaction.amount,
                    orderId=transaction.order_id,
                    transaction_id=trans_id)
                return JsonResponse({
                    "message": "ok",
                    "transaction_id": response
                },
                    status=200)

        except PaymentTransaction.DoesNotExist:
            return JsonResponse({
                "message": "Error. Transaction not found",
                "status": False
            },
                status=400)


class ConfirmView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        # save the data
       # request_data = json.dumps(request.data)
        request_data = request.data
        print("the data  is: " , request_data)
        body = request_data
        print("the body is: ",body)
        
        resultcode = body.get('stkCallback').get('ResultCode')
        # Perform your processing here e.g. print it out...
        if resultcode == 0:
            print('Payment successful')
            requestId = body.get('stkCallback').get('CheckoutRequestID')
            metadata = body.get('stkCallback').get('CallbackMetadata').get('Item')
            for data in metadata:
                if data.get('Name') == "MpesaReceiptNumber":
                    receipt_number = data.get('Value')
            transaction = PaymentTransaction.objects.get(
                checkout_request_id=requestId)
            if transaction:
                transaction.receipt_number = receipt_number
                transaction.is_finished = True
                transaction.is_successful = True
                transaction.save()

        else:
            print('unsuccessfull')
            requestId = body.get('stkCallback').get('CheckoutRequestID')
            transaction = PaymentTransaction.objects.get(
                checkout_request_id=requestId)
            if transaction:
                transaction.is_finished = True
                transaction.is_successful = False
                transaction.save()

        # Prepare the response, assuming no errors have occurred. Any response
        # other than a 0 (zero) for the 'ResultCode' during Validation only means
        # an error occurred and the transaction is cancelled
        message = {
            "ResultCode": 0,
            "ResultDesc": "The service was accepted successfully",
            "ThirdPartyTransID": "1237867865"
        }

        # Send the response back to the server
        return Response(message, status=HTTP_200_OK)

    def get(self, request):
        return Response("Confirm callback", status=HTTP_200_OK)


class ValidateView(APIView):
    permission_classes = [AllowAny, ]

    def post(self, request):
        # save the data
        request_data = request.data

        # Perform your processing here e.g. print it out...
        print("validate data" + request_data)

        # Prepare the response, assuming no errors have occurred. Any response
        # other than a 0 (zero) for the 'ResultCode' during Validation only means
        # an error occurred and the transaction is cancelled
        message = {
            "ResultCode": 0,
            "ResultDesc": "The service was accepted successfully",
            "ThirdPartyTransID": "1234567890"
        }

        # Send the response back to the server
        return Response(message, status=HTTP_200_OK)
    
    
class PaymentTransactionListView(generics.ListAPIView):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return PaymentTransaction.objects.filter(is_successful= False)

class SearchTransaction(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, trans_id, format=None):
        # Use a GET request and specify trans_id as a URL parameter
        # This allows you to retrieve a specific transaction directly
        transaction = get_object_or_404(PaymentTransaction, trans_id=trans_id)

        # Now, you can serialize the transaction and return it as a response
        serializer = PaymentTransactionSerializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
