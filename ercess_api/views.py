from django.shortcuts import render
from rest_framework.response import Response
from django.urls import reverse
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from django.conf import settings
from django.core.mail import  send_mail
from Ercesscorp.forms import RegistrationForm, UserForm, LoginForm, ForgotPasswordForm, ContactForm, ResetPassword,UpdateContact
from Ercesscorp.models import RegistrationData, BlogData, ContactData, Users
from .serializers import UserFormSerializer
from rest_framework.views import APIView
import hashlib
from rest_framework import status
from Ercesscorp.views import send_verification_email
class SignUp(APIView):

    def post(self,request):
        requestData = request.data
        fnameVal = request.data['firstname']
        lnameVal = request.data['lastname']
        emailVal = request.data['email']
        passVal = request.data['password']
        try:
            filterData = Users.objects.filter(user=emailVal)
            if len(filterData) == 0:
                        # save values into db
                pswd_encoded = hashlib.md5(passVal.encode('utf-8')).hexdigest()
                email_encoded = hashlib.md5(
                emailVal.encode('utf-8')).hexdigest()
                new_user = Users(user=emailVal, firstname=fnameVal, lastname=lnameVal,
                                        password=pswd_encoded, md5=email_encoded)
                new_user.save()
                send_verification_email(
                    request.get_host(), new_user.id, emailVal, fnameVal, lnameVal)
                messageData = {'user_id': new_user.id,'message': 'Congratulations! your account is successfully created. Please check your email and follow the instructions.',
                                       'responseType': 'success', 'messageType': 'success'}
                return Response(messageData,status=status.HTTP_200_OK)
            else:
                messageData = {'message': 'This account already exists in our record. Try to login.',
                                       'responseType': 'success', 'messageType': 'error'}
                return Response(messageData,status=status.HTTP_409_CONFLICT)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

class VerificationMail(APIView):
    def get(self,request):
        try:
            user_id = request.data['user_id']
            emailVal = request.data['email']
            firstname = request.data['firstname']
            lastname = request.data['lastname']
            send_verification_email(
                        request.get_host(), user_id, emailVal, firstname, lastname)
            messageData = {'message': 'Congratulations! Mail Sent','responseType': 'success', 'messageType': 'success'}
            return Response(messageData,status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
