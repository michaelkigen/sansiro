from django.shortcuts import render

from rest_framework import status,viewsets,views,mixins,generics
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
# from rest_framework.authentication import JSONWebTokenAuthentication

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import OrderedFoodSerializer,Menu_ObjectSerializer, CartSerializer,OrderIdSerializer, CategorySerializer,Update_cart_serializer,AddCartItemSerializer,Create_Cart_Serializer,ViewCartItemserializer,Order_Serializer
from .models import Menu_Object,Categories,Cart,Add_item_to_cart,Order,Orderd_Food
from .filters import Foodfilter
from Profile.models import Profile,Location
from Profile.serializers import LicationSerializer
from users.serializers import UserDetailedSerializer
from users.models import User
from records.views import recorder

from django.shortcuts import get_object_or_404

from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.utils import timezone
import cloudinary
from cloudinary import api
from django.conf import settings

from records.views import recorder
import cloudinary.uploader
from rest_framework.decorators import action
from payments.models import PaymentTransaction

from django.contrib.auth.decorators import user_passes_test

# Create your views here.
class MenuAPiView(viewsets.ModelViewSet):
    serializer_class = Menu_ObjectSerializer
    queryset = Menu_Object.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = Foodfilter
    parser_classes = (MultiPartParser,)

    @action(detail=False, methods=['POST'])
    def create_food(self, request):
        serializer = Menu_ObjectSerializer(data=request.data)
        if serializer.is_valid():
            # Upload food image to Cloudinary
            image_file = request.data.get('food_image')
            if image_file:
                cloudinary_response = cloudinary.uploader.upload(image_file)
                serializer.validated_data['food_image'] = cloudinary_response['secure_url']

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 
class MenuupdateAPiView(views.APIView):
    def get(self, request, food_id):
        try:
            food = Menu_Object.objects.get(food_id=food_id)
        except Menu_Object.DoesNotExist:
            return Response({'message': 'food not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = Menu_ObjectSerializer(food)
        return Response(serializer.data)

    def put(self, request, food_id):
        try:
            food = Menu_Object.objects.get(food_id=food_id)
        except Menu_Object.DoesNotExist:
            return Response({'message': 'Food not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = Menu_ObjectSerializer(food, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, food_id):
        try:
            food = Menu_Object.objects.get(food_id=food_id)
        except Menu_Object.DoesNotExist:
            return Response({'message': 'Food not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = Menu_ObjectSerializer(food, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, food_id):
        print('START')
        try:
            food = Menu_Object.objects.get(food_id=food_id)
        except Menu_Object.DoesNotExist:
            return Response({'message': 'Food not found'}, status=status.HTTP_404_NOT_FOUND)
        print('START 1')
        food.delete()
        print('START 2')
        print('DONE')
        return Response({'message': 'Food deleted'}, status=status.HTTP_200_OK)


# class MenuupdateAPiView(viewsets.ModelViewSet):
#     serializer_class = Menu_ObjectSerializer
#     queryset = Menu_Object.objects.all()
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = Foodfilter
#     parser_classes = (MultiPartParser,)

#     @action(detail=True, methods=['PUT'])
#     def update_food(self, request, pk):
#         menu_object = self.get_object()
#         serializer = Menu_ObjectSerializer(menu_object, data=request.data, partial=True)
#         if serializer.is_valid():
#             # Upload food image to Cloudinary if provided
#             image_file = request.data.get('food_image')
#             if image_file:
#                 cloudinary_response = cloudinary.uploader.upload(image_file)
#                 serializer.validated_data['food_image'] = cloudinary_response['secure_url']

#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     @action(detail=True, methods=['DELETE'])
#     def destroy(self, request, pk):
#         print("checking if the is in the database")
#         food = Menu_Object.objects.filter(food_id = pk)
#         print("db checked")
#         if not food:
#             return Response({"error":"enter correct id"}, status=status.HTTP_400_BAD_REQUEST)
#         print("delete starting")
#         food.delete()
#         print("deleted")
#         return Response({"success":"deleted!!"}, status=status.HTTP_200_OK)
    
# class CategoriesAPiView(viewsets.ModelViewSet):
    
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     serializer_class =CategorySerializer
#     queryset=  Categories.objects.all()
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['category']    
    

'''class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
   # permission_classes = [IsAuthenticated] # Add this line

   

class AddToCartViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        cart_pk = self.kwargs['']
        return Add_item_to_cart.objects.filter(cart_id=cart_pk)
    serializer_class = AddToCartSerializer

class Add_to_cart(viewsets.ModelViewSet):
    serializer_class = AddToCartSerializer
    queryset = Add_item_to_cart.objects.all()'''
    
class CartViewSet(viewsets.ModelViewSet):
    
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Require authentication for all actions

    def get_queryset(self):
        user = self.request.user  # Get the currently logged-in user
        return Cart.objects.filter(user=user)
  

class AddToCartViewSet(viewsets.ModelViewSet):
    
    http_method_names = ['get','post','patch','delete']
    
    def get_queryset(self):
        user = self.request.user
        cart_id = user.cart.cart_id
        return Add_item_to_cart.objects.filter(cart_id = cart_id )

    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        
        elif self.request.method == 'PATCH':
            return Update_cart_serializer
        
        return ViewCartItemserializer
    
    def get_serializer_context(self):
        user = self.request.user
        cart_id = user.cart.cart_id
        return {'cart_id': cart_id}
    
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        cart_id = instance.cart_id

        super().destroy(request, *args, **kwargs)

        remaining_items = Add_item_to_cart.objects.filter(cart_id=cart_id)
        serializer = self.get_serializer(remaining_items, many=True)
        return Response(serializer.data)

    
class CheckoutView(views.APIView):
    def post(self, request):
        # Perform the payment process here
        # If the payment is successful, continue to the next step

        cart = request.user.cart
        order = cart.create_order()
        
        serializer = Order_Serializer(order)
        return Response(serializer.data)
    
    def get(self, request):
        try:
            user = self.request.user
            orders = Order.objects.filter(user=user)

            if not orders:
                return Response({'detail': 'No orders found.'}, status=status.HTTP_404_NOT_FOUND)

            response_data = []

            for order in orders:
                ordered_food = Orderd_Food.objects.filter(order=order)
                ordered_food_serializer = OrderedFoodSerializer(ordered_food, many=True)
                order_serializer = Order_Serializer(order)
                orderId = order_serializer.data['order_id']
                trans = PaymentTransaction.objects.filter(order_id=orderId).first()
                user_serializer = UserDetailedSerializer(user)

                if trans:
                    order_data = {
                        'order_id': order_serializer.data['order_id'],
                        'trans_id': trans.trans_id,
                        'status': order_serializer.data['state'],
                        'created_at': order_serializer.data['created_at'],
                        'total': order_serializer.data['total'],
                        'is_canceled': order_serializer.data['is_canceled'],
                        'delivered_at': order_serializer.data['delivered_at'],
                        'payment_mode': order_serializer.data['payment_mode'],
                        'ordered_food': ordered_food_serializer.data,
                        'user': user_serializer.data
                    }
                    response_data.append(order_data)
                else:
                    order_data = {
                        'order_id': order_serializer.data['order_id'],
                        'status': order_serializer.data['state'],
                        'created_at': order_serializer.data['created_at'],
                        'total': order_serializer.data['total'],
                        'is_canceled': order_serializer.data['is_canceled'],
                        'delivered_at': order_serializer.data['delivered_at'],
                        'payment_mode': order_serializer.data['payment_mode'],
                        'ordered_food': ordered_food_serializer.data,
                        'user': user_serializer.data
                    }
                    response_data.append(order_data)

            return Response(response_data)
        except Exception as e:
            print(f"Error in get request: {str(e)}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class Orderdetailed(views.APIView):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Query does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        ordered_food = Orderd_Food.objects.filter(order=order)
        ordered_food_serializer = OrderedFoodSerializer(ordered_food, many=True)
        order_serializer = Order_Serializer(order, many=False)

        if order:
            user = order_serializer.data['user']
            user_serializer = UserDetailedSerializer(user)
            phone = user_serializer.data['phone_number']

            try:
                person = User.objects.get(phone_number=phone)
            except User.DoesNotExist:
                return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            profile = Profile.objects.filter(user=person.id).first()
            location = Location.objects.filter(userProfile=profile.profile_id).first()

            loc_serializer = LicationSerializer(location)  # Assuming you have a LocationSerializer

            response_data = {
                'order_id': order_serializer.data['order_id'],
                'status': order_serializer.data['state'],
                'created_at': order_serializer.data['created_at'],
                'is_canceled': order_serializer.data['is_canceled'],
                'user': user_serializer.data,
                'ordered_food': ordered_food_serializer.data,
                'location': loc_serializer.data
            }

            return Response(response_data)
        else:
            return Response({'detail': 'No order found.'}, status=status.HTTP_404_NOT_FOUND)

        
        
    def patch(self, request, order_id):
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Query does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = Order_Serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Check if is_canceled is being patched to True and state is "p"
        if serializer.validated_data.get("is_canceled") and serializer.validated_data.get("state") == "p":
            serializer.save()
            order.state = 'f'
            order.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Check if state is being patched to "c"
        elif serializer.validated_data.get("state") == "c":
            # Call your custom function (e.g., record_function)
            
            serializer.save()
            data = {
                'order_id': serializer.data['order_id'],
                'state': serializer.data['state'],
                'created_at': serializer.data['created_at'],
                'is_canceled': serializer.data['is_canceled'],
                'total': serializer.data['total'],
                'ordered_food': serializer.data['ordered_food']
            }
            record = recorder(data)
            print(record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif serializer.validated_data.get("state") == "d":
            # Call your custom function (e.g., record_function)
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif serializer.validated_data.get("location") != "null":
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        # If none of the conditions are met, return an appropriate response
        return Response({'detail': 'Invalid operation for the provided data.'}, status=status.HTTP_400_BAD_REQUEST)


class ProcessOrderView(views.APIView):
    def post(self, request, format=None):
        serializer = OrderIdSerializer(data=request.data)
        user = self.request.user
        user_profile = Profile.objects.get(user= user)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            user = self.request.user
            try:
                order = Order.objects.get(order_id=order_id)
            except Order.DoesNotExist:
                return Response({'detail': 'Order not found.'}, status=status.HTTP_404_NOT_FOUND)
            
            ordered_food_items = order.ordered_food.all()
            
            for ordered_food in ordered_food_items:
                if not ordered_food.food.is_avilable:
                    # Convert food price to points in a 1:10 ratio
                    points_to_add = ordered_food.food.price * 5
                    
                    # Update user's profile with points
                    user_profile = Profile.objects.get(user= user)
                    user_profile.points += int(points_to_add)
                    user_profile.save()
            
            return Response({'detail': 'Order processed successfully.'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def is_admin(user):
    return user.is_authenticated and user.is_admin


# @user_passes_test(is_admin)    
class OrdererdFood(views.APIView):
    def get(self, request):
        try:
            orders = Order.objects.all()
            order_count = orders.count()
            order_serializer = Order_Serializer(orders, many=True)
            response = {
                "order_count":order_count,
                "orders":order_serializer.data
            }
            return Response(response)
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Error: {str(e)}")
            return Response({'detail': 'Internal Server Error.'}, status=status.HTTP_401_UNAUTHORIZED)
from rest_framework.decorators import api_view
       
@api_view(['POST'])
@user_passes_test(is_admin)
def webhook_notification(request):
    # Process the incoming webhook payload
    data = request.data
    # Notify the admin about the new order or perform any other desired actions
    print("New order notification received:", data)
    return Response({"status": "Webhook received successfully"})




