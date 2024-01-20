from rest_framework import serializers
from .models import  DailyRecord

        
class DailyRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyRecord
        fields = [
            "dailyrecord_id",
            "measuredFood",
            "expectedQuantity",
            "foodName",
            "quantity",
            "amount",
            "total_amount",
            "date",
        ]
        extra_kwargs = {
            "dailyrecord_id": {"read_only": True},
            "date": {"read_only": True},
        }
