from django.urls import path
from .views import AggregatedDailyRecordView,Dailyrecordviews,Dailydeatiled

urlpatterns = [
    path("w_m_record/",AggregatedDailyRecordView.as_view(), name="weeklymonthly"),
    path("dailyrecord/",Dailyrecordviews.as_view(), name="daily"),
    path("dailyrecord/<uuid:dailyrecord_id>/",Dailydeatiled.as_view(), name="daily")
]
