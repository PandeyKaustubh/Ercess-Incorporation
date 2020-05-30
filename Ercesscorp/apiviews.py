from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import  status
from rest_framework import generics
# from django.contrib.auth.models import User
from django.contrib.auth import  authenticate
from .models import RegistrationData ,BlogData
from  .serializers import  RegistrationSerializer , BlogDataSerializer, UserSerializer
from django.contrib.auth.decorators import login_required



class BlogDetails(generics.ListCreateAPIView):
    queryset = BlogData.objects.all()
    serializer_class = BlogDataSerializer


class BlogSpecific(generics.RetrieveDestroyAPIView):
    queryset = BlogData.objects.all()
    serializer_class = BlogDataSerializer


class Reg(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    queryset = RegistrationData
    serializer_class =RegistrationSerializer

# class UserCreate(generics.CreateAPIView):
#     authentication_classes = ()
#     permission_classes = ()
#     queryset = User
#     serializer_class = UserSerializer

class LoginView(APIView):

    permission_classes = ()

    def post(self, request, ):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)
