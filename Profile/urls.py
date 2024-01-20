from django.urls import path
from .views import ProfileView,LocationView

urlpatterns = [
    path("", ProfileView.as_view()),
    path("location/", LocationView.as_view())
    
]
