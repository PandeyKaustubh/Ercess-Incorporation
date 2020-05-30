from rest_framework.authtoken.models import Token
from rest_framework import  serializers
from rest_framework.views import  APIView
from rest_framework.response import  Response
from rest_framework import  status


from .models import *
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):

    class Meta :
        model = User
        fields = ('username', 'password', 'email')
        extra_kwargs = {'password': {'write_only': True}}


class RegistrationSerializer(serializers.ModelSerializer):

    user = UserSerializer(required=True)
    class Meta :
        model = RegistrationData
        fields = ('user','mobile','location','gender')
    def create(self, validated_data):

        user = validated_data['user']
        usera = User.objects.create_user(username=user['username'],
                                        email=user['email'],
                                        password=user['password'])
        usera.save()
        # user.set_password(validated_data['password'])     #to set raw password
        re = RegistrationData(
            user=usera,
            mobile=validated_data['mobile'] ,
            location=validated_data['location'],
            gender= validated_data['gender']
        )
        re.save()
        Token.objects.create(user=usera)
        return re



class BlogDataSerializer(serializers.ModelSerializer):

    class Meta :
        model = BlogData
        fields = '__all__'



