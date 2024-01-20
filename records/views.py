from django.shortcuts import render
from rest_framework import views,status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from .models import DailyRecord
from .serializers import DailyRecordSerializer
from Profile.models import Profile
from users.models import User
from datetime import datetime, timedelta
from menu.models import Menu_Object
from django.utils import timezone
from menu.models import Order
# ...
# Create your views here.
from django.db import transaction
from django.utils import timezone
from .models import DailyRecord

def record_function(orderid):
    try:
        order = Order.objects.get(order_id=orderid)
    except Order.DoesNotExist:
        return ValueError

    records = []

    with transaction.atomic():
        # Iterate through ordered food items
        for ordered_food in order.ordered_food.all():
            food_name = ordered_food.food.food_name  # Assuming there's a 'name' field in Menu_Object model
            quantity = ordered_food.quantity
            amount = ordered_food.sub_total  # Assuming sub_total represents the amount for the food item

            # Check if a record already exists for the food and date
            existing_record = DailyRecord.objects.filter(
                food=food_name,
                date__date=timezone.now().date(),
            ).first()

            # If the record exists, increment quantity and amount
            if existing_record:
                existing_record.quantity += quantity
                existing_record.amount += amount
                existing_record.save()
                records.append(existing_record)
            else:
                # If the record does not exist, create a new record
                new_record = DailyRecord.objects.create(
                    food=food_name,
                    quantity=quantity,
                    amount=amount,
                )
                records.append(new_record)

    return records




def convert_to_points(unavilable_food,user):
    phone_number = user["phone_number"]
    print("User ",phone_number)
    try:
        user = User.objects.get(phone_number=phone_number)
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return Response({'error': 'profile not found.'}, status=status.HTTP_404_NOT_FOUND)
    pnts = int(unavilable_food) * 5
    print("Pointd ",pnts)
    profile.points +=pnts
    profile.save()


def recorder(food):
    current_time = timezone.now()  # Get the current date and time
    print("FOOD :", food)
    
    for item in food['ordered_food']:
        food_name = item['food']['food_name']
        print("FOOD NAME : ", food_name)
        quantity = item['quantity']
        print("QUANTITY : ", quantity)
        sub_total = item['sub_total']
        print("SUB TOTAL : ", sub_total)
        total = food['total']
        print("TOTAL : ", total)

        try:
            # Attempt to retrieve the latest DailyRecord for the given food_name
            record = DailyRecord.objects.filter(foodName=food_name).latest('date')
        except DailyRecord.DoesNotExist:
            # If no DailyRecord exists, create a new one
            record = DailyRecord(foodName=food_name, quantity=0, amount=0, date=current_time)

        # Calculate the time difference between the current time and the record's date
        time_difference = current_time - record.date

        # If the time difference exceeds 23 hours, create a new DailyRecord entry
        if time_difference.total_seconds() >= 23 * 3600:
            record = DailyRecord(foodName=food_name, quantity=quantity, amount=sub_total, date=current_time)

        # Update the quantity and amount, providing default values if they are None
        record.quantity = record.quantity or 0
        record.amount = record.amount or 0
        record.quantity += quantity
        record.amount += sub_total
        record.total_amount += total

        record.save()
    order_id = food['order_id']
    try:
        order = Order.objects.get(order_id= order_id)
        order.delivered_at = current_time
        order.save()
    except Order.DoesNotExist:
        print("error")
            
    return True

        

         
class Dailyrecordviews(views.APIView):
    def get(self,request):
        try:
            dr = DailyRecord.objects.all()
        except DailyRecord.DoesNotExist:
            return Response({'error':'query dies not exists'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DailyRecordSerializer(dr,many =True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        data = request.data
        # Ensure that 'food' and 'measuredFood' are present in the request data
        if 'food' not in data or 'measuredFood' not in data:
            return Response({'error': 'Both "food" and "measuredFood" fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new DailyRecord instance with the provided data
        serializer = DailyRecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Dailydeatiled(views.APIView):
    def get(self,request,dailyrecord_id):
        try:
            dr = DailyRecord.objects.filter(dailyrecord_id = dailyrecord_id).first()
        except DailyRecord.DoesNotExist:
            return Response({'error':'query dies not exists'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DailyRecordSerializer(dr,many =True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self,request,dailyrecord_id):
        try:
            dr = DailyRecord.objects.filter(dailyrecord_id = dailyrecord_id).first()
        except DailyRecord.DoesNotExist:
            return Response({'error':'query dies not exists'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = DailyRecordSerializer(dr,data=request.data , partial= True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    
    

class AggregatedDailyRecordView(views.APIView):
    def get(self, request):
        # Calculate the date range for the past week and month
        today = datetime.now().date()
        one_week_ago = today - timedelta(days=7)
        one_month_ago = today - timedelta(days=30)

        # Filter daily records for the past week and month
        weekly_records = DailyRecord.objects.filter(date__gte=one_week_ago, date__lte=today)
        monthly_records = DailyRecord.objects.filter(date__gte=one_month_ago, date__lte=today)

        # Serialize the data
        weekly_serializer = DailyRecordSerializer(weekly_records, many=True)
        monthly_serializer = DailyRecordSerializer(monthly_records, many=True)

        # Calculate weekly and monthly totals
        weekly_total_quantity = sum(record.quantity for record in weekly_records)
        weekly_total_amount = sum(record.amount for record in weekly_records)
        monthly_total_quantity = sum(record.quantity for record in monthly_records)
        monthly_total_amount = sum(record.amount for record in monthly_records)

        response_data = {
            'weekly_records': weekly_serializer.data,
            'monthly_records': monthly_serializer.data,
            'weekly_total_quantity': weekly_total_quantity,
            'weekly_total_amount': weekly_total_amount,
            'monthly_total_quantity': monthly_total_quantity,
            'monthly_total_amount': monthly_total_amount,
        }

        return Response(response_data, status=status.HTTP_200_OK)
