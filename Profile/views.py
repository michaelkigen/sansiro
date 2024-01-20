from rest_framework import generics, status,views
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from cloudinary.exceptions import Error
from users.models import User
from rest_framework import serializers
from .serializers import ProfileSerializer, LicationSerializer
from .models import Profile,Location

class ProfileView(generics.CreateAPIView):
    parser_classes = [MultiPartParser]
    serializer_class = ProfileSerializer
    
    def get_object(self):
        user = self.request.user
        profile = Profile.objects.get(user = user)
        # Access all the payment transactions related to the profile
        return profile


    
    def create(self, request, *args, **kwargs):
        try:
            profile = self.get_object()
            serializer = self.get_serializer(profile, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()  # Update the existing profile
        except Profile.DoesNotExist:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()  # Create a new profile
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
  
    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        # return Response({"points":str(profile.points),"transactions":str(profile.payments),"pic":serializer.data},status= status.HTTP_200_OK)
        return Response(serializer.data,status= status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        profile = self.get_object()
        profile.delete()
        return Response({"message":"profile picture removed "},status=status.HTTP_204_NO_CONTENT)
    
    
from rest_framework.permissions import IsAuthenticated


class LocationView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            locations = Location.objects.all()
        except Location.DoesNotExist:
            return Response({'detail': 'Locations not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LicationSerializer(locations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = LicationSerializer(data=request.data, context={'request': request})

        try:
            serializer.is_valid(raise_exception=True)
       
            # Correctly access the Profile from the authenticated user
            serializer.validated_data['userProfile'] = request.user.profile
            print(serializer.validated_data['userProfile'])

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            # If validation fails, return details about the error
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log the exception for debugging purposes
            print(f"Error: {str(e)}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
