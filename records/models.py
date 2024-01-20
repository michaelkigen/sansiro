from django.db import models
import uuid

# Create your models here.
    
class DailyRecord(models.Model):
    dailyrecord_id=models.UUIDField(default=uuid.uuid4, primary_key= True , auto_created=True, editable=True)
    measuredFood = models.CharField( max_length=100,null = True)
    expectedQuantity = models.CharField(max_length=100,null= True)
    foodName = models.CharField( max_length=100)
    quantity = models.IntegerField(default=0)  # Set a default value
    amount = models.IntegerField(default=0)
    total_amount = models.IntegerField(default=0)
    date = models.DateTimeField( auto_now_add=True)
