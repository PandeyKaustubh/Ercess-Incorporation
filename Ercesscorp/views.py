from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.conf import settings
import logging
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotFound
from django.core import serializers
from django.urls import reverse
from django.template import RequestContext, Context, loader
from hashlib import md5
from dashboard.forms import Articles2Form, BoostEventForm
from html import unescape
from django.utils.dateparse import parse_date
import secrets
import time
import os
import re
from PIL import Image
from django.core.files.storage import FileSystemStorage
from datetime import datetime
import itertools
from django.contrib.staticfiles.urls import static
from dashboard.models import AdminActionLog, EventProcesses, EventVerificationResult, Rsvp, StatusPromotionTicketing, PartnerSites, StatusOnChannel, BoostEvent, EventStatusOnChannel, FinanceStandardCharges, PackageSales, BankDetails, AnnouncementsAccess, TicketDiscounts, ReferrerCashbackInfo, ReferrerCashbackTokens, TicketSalesReference, ShortUrlTracker, CampaignTemplates, Leads, CampaignStatus, ExpectationsFeedbacks
from django.contrib import messages
import traceback
from random import randint

from .forms import RegistrationForm, UserForm, LoginForm, ForgotPasswordForm, ContactForm, ResetPassword,UpdateContact
from .models import RegistrationData, BlogData, ContactData, Users
from dashboard.models import Rsvp, StatusPromotionTicketing, Articles2, Tickets, TicketsSale, AdminEventAssignment, Admin, StatusOnChannel, Categories, Topics, CategorizedEvents, AboutCountries, EventEditLogs, AttendeeFormBuilder, AttendeeFormTypes, AttendeeFormOptions

from django.utils import timezone
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.hashers import make_password, check_password
import hashlib
from .models import UserRegistrationToken
import uuid
from datetime import datetime as dt
######## to manage error of MultipleObjectsReturned ###########
from django.core.exceptions import MultipleObjectsReturned
from django.template.loader import render_to_string

from django.conf import settings as conf_settings
from django.db.models import Max
# from django_xhtml2pdf.utils import generate_pdf
from weasyprint import HTML
from dashboard.api.serializers import Articles2Serializer, StatusPromotionTicketingSerializer, CategorizedEventsSerializer 
from dashboard.api.views import createDiscountCoupon
import shutil
from dashboard import url_shortner
import csv
from django.views.generic import View,TemplateView
import json
from os import listdir
from django.conf import settings
from os.path import isfile, join
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail,EmailMultiAlternatives,EmailMessage

email_sent_from = settings.EMAIL_HOST_USER

flag = 0
l = []
email_verify_dict = {}


logging.basicConfig(filename='test.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

###########################################
# # from pytz import timezone
# from django.utils import timezone
# import datetime

# # import pytz

# print(' ########### 12345 ############ ')
# # timezone.activate(pytz.timezone("Asia/Singapore"))
# print(' >>>>>>>>> ',datetime.datetime.now())
# print(' >>>>>>>>> ',timezone.now())
# print(' >>>>>>>>> ', timezone.get_current_timezone())

###########################################


def send_verification_email(host_url_param, user_id_param, user_email_param, firstname_param, lastname_param):
    try:
        email_token = str(uuid.uuid4()) + str(user_id_param)
        # save token into db
        currentTime = dt.now(tz=timezone.utc)

        # UserRegistrationToken.objects.filter(user_email=emailVal)
        user_registration_token_filter_data = UserRegistrationToken.objects.filter(
            user_email=user_email_param)
        if len(user_registration_token_filter_data) == 0:
            UserRegistrationToken.objects.create(
                user_email_token=email_token, user_email=user_email_param, user_email_token_created_on=currentTime)
        else:
            UserRegistrationToken.objects.filter(user_email=user_email_param).update(
                user_email_token=email_token, user_email_token_created_on=currentTime)
        # ends here ~ save token into db

        verify_url = 'http://' + host_url_param + \
            '/live/verify_email/' + email_token + '/'
        # send email
        html_message = loader.render_to_string('static/common/signup_verification.html',
                                               {
                                                   'firstname': firstname_param,
                                                   'lastname': lastname_param,
                                                   'verify_url': verify_url
                                               })
        print(email_sent_from)
        send_mail('Verify your email - Ercess Live', 'message', email_sent_from, [
                  user_email_param], fail_silently=False, html_message=html_message)
        # ends here ~ send email

    except Exception as e:
        print('error is ', e)


@csrf_exempt
def registration(request):
    regerr = False
    pass_no_match = False
    mail_no_match = False
    auth_email_failed = False
    submitted = False
    sec_code = None
    errormail = False
    x = 0
    if request.method == 'POST':
        try:
            # read request data
            requestData = request.body
            requestDataDecode = requestData.decode('utf8').replace("'", '"')
            requestDataJson = json.loads(requestDataDecode)
            # ends here ~ read request data

            # set value into variable
            fnameVal = requestDataJson['fnameVal']
            lnameVal = requestDataJson['lnameVal']
            locVal = requestDataJson['locVal']
            emailVal = requestDataJson['emalVal']
            passVal = requestDataJson['passVal']
            # ends here ~ set value into variable

            # test code
            # Users.objects.filter().exclude(id=1).delete()
            # UserRegistrationToken.objects.filter(user_email=emailVal).delete()
            # ends here ~ test code

            filterData = Users.objects.filter(user=emailVal)
            if len(filterData) == 0:
                # save values into db
                pswd_encoded = hashlib.md5(passVal.encode('utf-8')).hexdigest()
                email_encoded = hashlib.md5(
                    emailVal.encode('utf-8')).hexdigest()
                new_user = Users(user=emailVal, firstname=fnameVal, lastname=lnameVal,
                                 location=locVal, password=pswd_encoded, md5=email_encoded)
                new_user.save()
                # ends here ~ save values into db

                # email_token = str(uuid.uuid4()) + str(new_user.id)

                send_verification_email(
                    request.get_host(), new_user.id, emailVal, fnameVal, lnameVal)
                '''
                html_message = loader.render_to_string('static/common/signup_verification.html',
                     {
                     'firstname': 'firstname_param',
                     'lastname': 'lastname_param',
                     'verify_url':'verify_url'
                     })
                '''
             #   send_mail('subject','message',email_sent_from,['mybooks0101@gmail.com'],fail_silently=False) #,html_message=html_message)
                # # ends here ~ send email

                messageData = {'message': 'Congratulations! your account is successfully created. Please check your email and follow the instructions.',
                               'responseType': 'success', 'messageType': 'success'}

            else:

                messageData = {'message': 'This account already exists in our record. Try to login.',
                               'responseType': 'success', 'messageType': 'error'}


#            messageData = {'as':'as'}
            return HttpResponse(json.dumps(messageData))
        except Exception as e:
            print('error is', e)
            ############### new code ~ Date: 21 april 2019 #############
            # @author Shubham
            # return message
            messageData = {'message': e,
                           'responseType': 'error', 'messageType': 'error'}
            return HttpResponse(json.dumps(messageData))
            ################ ends here ~  new code ~ Date: 21 april 2019 #############

    else:
        form1 = UserForm()
        form2 = RegistrationForm()
        if 'regerr' in request.GET:
            regerr = True
        if 'pass_no_match' in request.GET:
            pass_no_match = True
        if 'mail_no_match' in request.GET:
            mail_no_match = True
        if 'submitted' in request.GET:
            submitted = True
        if 'errormail' in request.GET:
            errormail = True
        if 'auth_email_failed' in request.GET:
            auth_email_failed = True
        return render(request, 'registration.html', {'form1': form1,
                                                     'form2': form2,
                                                     'regerr': regerr,
                                                     'pass_no_match': pass_no_match,
                                                     'mail_no_match': mail_no_match,
                                                     'errormail': errormail,
                                                     'submitted': submitted,
                                                     'auth_email_failed': auth_email_failed})


def verify_mail(request, slug):
    try:
        try:
            filterData = UserRegistrationToken.objects.get(
                user_email_token=slug)
            filterTime = filterData.user_email_token_created_on
        except Exception as e:
            print('verify_email error', e)
            messageData = {'message': 'Token is invalid. Please get a new confirmation mail from your dashboard.',
                           'responseType': 'success', 'token_type': 'email'}
            # return HttpResponse(json.dumps(messageData))
            context = {}
            context['messageData'] = messageData
            return render(request, 'email_password_template.html', context)

        if (filterTime == ''):
            messageData = {'message': 'Token is invalid. Please get a new confirmation mail from your dashboard.',
                           'responseType': 'success', 'token_type': 'email'}
        else:
            tokenCreateTime = filterTime.strftime("%Y-%m-%d %H:%M:%S")
            currentTime = dt.now().strftime("%Y-%m-%d %H:%M:%S")

            fmt = '%Y-%m-%d %H:%M:%S'
            tokenCreateTimeNew = dt.strptime(tokenCreateTime, fmt)
            currentTimeNew = dt.strptime(currentTime, fmt)
            print(tokenCreateTimeNew)
            print(currentTimeNew)
            minutesDifference = currentTimeNew - tokenCreateTimeNew
            diff_minutes = (minutesDifference.days * 24 * 60) + \
                (minutesDifference.seconds / 60)

            if diff_minutes >= 5:
                messageData = {'message': 'Token is invalid. Please get a new confirmation mail from your dashboard.',
                               'responseType': 'success', 'token_type': 'email'}
                # if (filterData.user_password_token == ''):
                #     UserRegistrationToken.objects.filter(user_email=filterData.user_email).delete()
                # else:
                #     UserRegistrationToken.objects.filter(user_email=filterData.user_email).update(user_email_token='',user_email_token_created_on='')
            else:
                Users.objects.filter(
                    user=filterData.user_email).update(status='active')
                filterUserTable = Users.objects.get(user=filterData.user_email)
                if (filterData.user_password_token == ''):
                    UserRegistrationToken.objects.filter(
                        user_email=filterData.user_email).delete()
                else:
                    UserRegistrationToken.objects.filter(user_email=filterData.user_email).update(
                        user_email_token='', user_email_token_created_on='')
                html_message = loader.render_to_string('static/common/welcome_email_template.html', {
                    'firstname': filterUserTable.firstname,
                    'lastname': filterUserTable.lastname,
                })

                # send welcome template
                send_mail('Welcome to Ercess Live', 'message', email_sent_from, [
                          filterData.user_email], fail_silently=False, html_message=html_message)
                messageData = {'message': 'We were successful to verify your email address. You can proceed with login now.',
                               'responseType': 'success', 'token_type': 'email'}
                # ends here ~ send welcome template

        # return HttpResponse(json.dumps(messageData))
        context = {}
        context['messageData'] = messageData
        return render(request, 'email_password_template.html', context)
    except Exception as e:
        print('error is ', e)
        messageData = {'message': 'Something went wrong. Please try again.',
                       'responseType': 'error', 'token_type': 'email'}
        context = {}
        context['messageData'] = messageData
        return render(request, 'email_password_template.html', context)



''' 
def registration(request):
    print('in view')
    regerr =False
    pass_no_match = False
    mail_no_match = False
    auth_email_failed = False
    submitted = False
    sec_code = None
    errormail = False
    x =0
    if request.method == 'POST':
        form1  = UserForm(request.POST)
        form2 = RegistrationForm(request.POST)
        if form1.is_valid() and form2.is_valid() :
            print('after validation')
            firstname = request.POST.get('firstname','')
            lastname = request.POST.get('lastname','')
            email = request.POST.get('email','')
            cemail = request.POST.get('confirmmail','')
            password = request.POST.get('password','')
            re_enter_password = request.POST.get('reenter_password','')

            # print(firstname, lastname , email ,cemail ,password , re_enter_password)
            if email != cemail :
                return redirect('/live/signup?mail_no_match=True')
            if password!= re_enter_password :
                return redirect('/live/signup?pass_no_match=True')

            data = User.objects.filter(email=email)
            print(data)
            if not data :
                try:
                    user = User.objects.create_user(username=email ,
                                                    first_name = firstname ,
                                                    last_name = lastname ,
                                                    email=email ,
                                                    password=password)
                    user.save()
                    u = authenticate(username=email, password=password , email=email)

                    # print('before auth save')
                    print(u.save())
                    # print('after auth save')
                    # mobile = request.POST.get('mobile','')
                    gender = request.POST.get('gender', '')
                    location = request.POST.get('location', '')
                    reg = RegistrationData(
                        user=user,
                        gender= gender,
                        location= location
                    )
                    x = reg.save()
                    pswd_encoded = md5(password.encode('utf-8')).hexdigest()
                    new_user = Users(user=email, firstname = firstname,
                                     lastname = lastname, password=pswd_encoded,
                                     gender= gender, location= location)

                    new_user.save()
                except Exception as e:
                    print('exception in register')
                    print(e)
                    return redirect('/live/signup?regerr=True')
            else:
                return redirect('/live/signup?regerr=True')
            if x is not None:
                return redirect('/live/signup?regerr=True')
            else :
                try:
                    sec_code = get_sec_code()
                    print('-------------')
                    print(sec_code)
                    res = send_mail('Verify email', 'http://127.0.0.1:8000/live/verify_email/?email='+email+'&token='+sec_code + '\n\n\n' + 'verify your email !!!',
                                    'tickets@ercess.com', [email, ])
                except Exception as e:
                    #print(res)
                    print(e)
                    return redirect('/live/signup?errormail=True')
                else:
                    # add email and seccode to dict
                    set_key_email(email, sec_code)
                    return redirect('/live/signup?submitted=True')
        form1 = UserForm()
        form2 = RegistrationForm()
        return render(request, 'registration.html', {'form1': form1, 'form2': form2})
    else :
        form1 = UserForm()
        form2 = RegistrationForm()
        if 'regerr' in request.GET:
            regerr = True
        if 'pass_no_match' in request.GET:
            pass_no_match = True
        if 'mail_no_match' in request.GET:
            mail_no_match = True
        if 'submitted' in request.GET:
            submitted = True
        if 'errormail' in request.GET:
            errormail = True
        if 'auth_email_failed' in request.GET:
            auth_email_failed = True
        return render(request , 'registration.html',{'form1':form1 ,
                                                     'form2':form2 ,
                                                     'regerr':regerr,
                                                     'pass_no_match':pass_no_match,
                                                     'mail_no_match':mail_no_match ,
                                                     'errormail':errormail,
                                                     'submitted':submitted ,
                                                     'auth_email_failed':auth_email_failed})

'''


def set_key_email(email, sec_code):
    key1 = str(email)
    key2 = key1 + 'sc'
    email_verify_dict[key1] = email
    email_verify_dict[key2] = sec_code


'''
def verify_mail(request):
    if request.method == 'GET':
        if 'token' in request.GET:
            token = request.GET.get('token', '')
        if 'email' in request.GET:
            email = request.GET.get('email', '')

        key1 = str(email)
        key2 = key1 + 'sc'

        if key1 in email_verify_dict and key2 in email_verify_dict:
            print('exist')
            #set value 1 in db and redirect to login
            u = User.objects.get(email=email)
            print(u)
            r = RegistrationData.objects.get(user_id=u.pk)
            r.verify = 1
            r.save()

            print('pop out keys')

            print(email_verify_dict.pop(key1))
            print(email_verify_dict.pop(key2))

            return  redirect('/live/login?verified=True')
        else:
            print('no')
            #show error that authentication failed
            return redirect('/live/signup?auth_email_failed=True')

'''


@csrf_exempt
def loginview(request):
    print('>>>>>>>>>>> >>>>>>>>>>>>>> >>>>>>>>>>> >>>>>>>>>> >>>')
    print('>>>>>>>>>>> >>>>>>>>>>>>>> >>>>>>>>>>> >>>>>>>>>> >>>')
    print(request.path, request.GET.get('next'))
    # print(request.path,' ><><><><><><><>< ',request.META.get('HTTP_REFERER'))
    print('>>>>>>>>>>> >>>>>>>>>>>>>> >>>>>>>>>>> >>>>>>>>>> >>>')
    print('>>>>>>>>>>> >>>>>>>>>>>>>> >>>>>>>>>>> >>>>>>>>>> >>>')


    loginerror = False
    error = False
    verify_error = False
    verified = False
    mail = False
    contact = False
    submitted = False
    passchange = False
    if request.method == 'POST':
        requestData = request.body
        requestDataDecode = requestData.decode('utf8').replace("'", '"')
        requestDataJson = json.loads(requestDataDecode)

        email = requestDataJson['emalVal']
        password = requestDataJson['passVal']

        print('after login form validation')

        pswd_encoded = md5(password.encode('utf-8')).hexdigest()

        if Users.objects.filter(user=email).exists():

            if Users.objects.filter(user=email, password=pswd_encoded).exists():

                u = Users.objects.get(user=email)

                #status = u.status
                # if status=='active':
                request.session['username'] = email
                request.session['userid'] = u.id
                request.session['firstname'] = u.firstname
                print(request.session['firstname'],'================================')
                request.session['lastname'] = u.lastname

                request.session.modified = True
                # us = authenticate(username=email, password=password)
                # if us:
                #   next_url = request.GET.get('next')
                #  print(next_url)
                # if next_url:
                print(request)
                print(request.session.keys())
                messageData = {'url': '/live/dashboard/','responseType': 'success', 'messageType': 'success'}
                # messageData = {'url': '/live/dashboard/add-event','responseType': 'success', 'messageType': 'success'}
                return HttpResponse(json.dumps(messageData))
                # return HttpResponseRedirect('/live/dashboard/add-event')
                # return redirect('dashboard:step_one')
                # else:
                #   return redirect('dashboard:how')
                # else :
                #   messageData = {'message':'Verify your email','responseType':'success', 'messageType':'success'}
                #  return HttpResponse(json.dumps(messageData))
                # return redirect('/live/login?verify_error=True')
            else:
                messageData = {'message': 'Invalid details provided',
                               'responseType': 'success', 'messageType': 'error'}
                return HttpResponse(json.dumps(messageData))
                # return redirect('/live/login?error=True')
        else:
            messageData = {'message': 'Oops! this user does not exist in our record.',
                           'responseType': 'success', 'messageType': 'error'}
            return HttpResponse(json.dumps(messageData))
       # print('checkkkkkk----------------------------------------------')
       # print(form.errors)
        #form = LoginForm()
        # return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
        if 'loginerror' in request.GET:
            loginerror = True
        if 'error' in request.GET:
            error = True
        if 'mail' in request.GET:
            mail = True
        if 'contact' in request.GET:
            contact = True
        if 'submitted' in request.GET:
            submitted = True
        if 'passchange' in request.GET:
            passchange = True
        if 'verify_error' in request.GET:
            verify_error = True
        if 'verified' in request.GET:
            verified = True
        return render(request, 'login.html', {'form': form, 'loginerror': loginerror, 'error': error,
                                              'mail': mail, 'contact': contact,
                                              'submitted': submitted, 'passchange': passchange,
                                              'verify_error': verify_error,
                                              'verified': verified})


'''
def loginview(request):
    error = False
    verify_error = False
    verified = False
    mail = False
    contact =False
    submitted = False
    passchange = False
    if request.method == 'POST':
        form = LoginForm(request.POST)
        print('before validation')
        if form.is_valid():
            print('after validation')
            email = request.POST.get('email' ,'')
            password = request.POST.get('password', '')
            # print(username)
            # print(password)
            user = authenticate(username = email , password = password)
            # print('user in login view')
            print('user')
            print(user)
            if user :

                u = User.objects.get(email=email)
                print(u)
                r = RegistrationData.objects.get(user_id= u.pk )
                print('in views of ercess corp')
                verify = r.verify
                if verify:
                    print(r.submitted)
                    request.session['sub'] = r.submitted
                    print(request.session['sub'])
                    request.session['username'] = email
                    login(request, user)
                    return redirect('dashboard:how')
                else :
                    return redirect('/live/login?verify_error=True')
            else :
                return redirect('/live/login?error=True')
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
        if 'error' in request.GET:
            error = True
        if 'mail' in request.GET:
            mail = True
        if 'contact' in request.GET:
            contact = True
        if 'submitted' in request.GET:
            submitted = True
        if 'passchange' in request.GET:
            passchange = True
        if 'verify_error' in request.GET:
            verify_error = True
        if 'verified' in request.GET:
            verified = True
        return render(request, 'login.html', {'form': form ,'error':error ,
                                              'mail':mail ,'contact':contact ,
                                              'submitted':submitted ,'passchange':passchange,
                                              'verify_error':verify_error,
                                              'verified':verified})
'''
@csrf_exempt
def forgotPassword(request):
    try:
        errormail = False
        usernotexist = False
        res = 0
        if request.method == 'POST':
            try:
                # read request data
                requestData = request.body
                print('requestData', requestData)
                requestDataDecode = requestData.decode(
                    'utf8').replace("'", '"')
                requestDataJson = json.loads(requestDataDecode)
                # ends here ~ read request data

                # set value into variable
                emailVal = requestDataJson['emalVal']
                # ends here ~ set value into variable

                filterData = Users.objects.filter(user=emailVal)
                if len(filterData) == 0:
                    messageData = {'message': 'Oops! this user does not exist in our record.',
                                   'responseType': 'success', 'messageType': 'error'}
                else:
                    filterUserData = Users.objects.get(user=emailVal)
                    password_token = str(uuid.uuid4()) + str(filterUserData.id)

                    # save token into db
                    currentTime = dt.now().strftime("%Y-%m-%d %H:%M:%S")
                    user_registration_token_filter_data = UserRegistrationToken.objects.filter(
                        user_email=emailVal)
                    if len(user_registration_token_filter_data) == 0:
                        UserRegistrationToken.objects.create(
                            user_password_token=password_token, user_email=emailVal, user_password_token_created_on=currentTime)
                    else:
                        UserRegistrationToken.objects.filter(user_email=emailVal).update(
                            user_password_token=password_token, user_password_token_created_on=currentTime)
                    # ends here ~ save token into db

                    verify_url = 'http://' + request.get_host() + '/live/reset_password/' + \
                        password_token + '/'
                    # send email
                    html_message = loader.render_to_string('static/common/forget_password_template.html',
                                                           {
                                                               'verify_url': verify_url
                                                           })
                    print('emailVal', emailVal)
                    print('email_sent_from', email_sent_from)
                    send_mail('Reset Password - Ercess Live', 'message', email_sent_from,
                              [emailVal], fail_silently=False, html_message=html_message)
                    # ends here ~ send email

                    messageData = {'message': 'Please check your email to reset password.',
                                   'responseType': 'success', 'messageType': 'success'}

                return HttpResponse(json.dumps(messageData))

            except Exception as e:
                print('error is', e)
                form = ForgotPasswordForm()
                if 'errormail' in request.GET:
                    errormail = True
                if 'usernotexist' in request.GET:
                    usernotexist = True
                return render(request, 'fogotpassword.html', {'form': form, 'errormail': errormail, 'usernotexist': usernotexist})
        else:
            form = ForgotPasswordForm()
            if 'errormail' in request.GET:
                errormail = True
            if 'usernotexist' in request.GET:
                usernotexist = True
            return render(request, 'fogotpassword.html', {'form': form, 'errormail': errormail, 'usernotexist': usernotexist})
    except Exception as e:
        print('error is ', e)
        if 'errormail' in request.GET:
            errormail = True
        if 'usernotexist' in request.GET:
            usernotexist = True
        return render(request, 'fogotpassword.html', {'form': form, 'errormail': errormail, 'usernotexist': usernotexist})


@csrf_exempt
def setNewPassword(request):
    try:
        # read request data
        requestData = request.body
        requestDataDecode = requestData.decode('utf8').replace("'", '"')
        requestDataJson = json.loads(requestDataDecode)
        # ends here ~ read request data

        print(requestDataJson)
        # get all required values
        slugValue = requestDataJson['slugVal']
        passwordValue = requestDataJson['passVal']
        # ends here ~ get all required values

        # code for changed password
        try:
            filterData = UserRegistrationToken.objects.get(
                user_password_token=slugValue)
            pswd_encoded = hashlib.md5(
                passwordValue.encode('utf-8')).hexdigest()
            Users.objects.filter(user=filterData.user_email).update(
                password=pswd_encoded)
            # ends here ~ code for changed password

            if (filterData.user_email_token == ''):
                UserRegistrationToken.objects.filter(
                    user_email=filterData.user_email).delete()
            else:
                UserRegistrationToken.objects.filter(user_email=filterData.user_email).update(
                    user_password_token='', user_password_token_created_on='')
            messageData = {'url': '/live/login/', 'message': 'Your password was reset successfully.',
                           'responseType': 'success', 'token_type': 'password', 'messageType': 'success'}
            return HttpResponse(json.dumps(messageData))
        except Exception as e:
            messageData = {'message': 'Token is already used to reset your password.',
                           'responseType': 'success', 'token_type': 'password', 'messageType': 'error'}
            return HttpResponse(json.dumps(messageData))

    except Exception as e:
        raise


def resetPassword(request, slug):
    try:
        usernotexist = False
        passnotmatch = False
        if request.method == 'POST':
            pass
            # # read request data
            # requestData = request.body
            # requestDataDecode = requestData.decode('utf8').replace("'", '"')
            # requestDataJson = json.loads(requestDataDecode)
            # # ends here ~ read request data

            # print(requestDataJson)

        else:
            try:
                filterData = UserRegistrationToken.objects.get(
                    user_password_token=slug)
                filterTime = filterData.user_password_token_created_on
            except Exception as e:
                messageData = {'message': 'Your token is expired. Please try again.',
                               'responseType': 'success', 'token_type': 'password', 'messageType': 'error'}
                context = {}
                context['messageData'] = messageData
                return render(request, 'resetpassword.html', context)

            if (filterTime == ''):
                messageData = {'message': 'Your token is expired. Please try again.',
                               'responseType': 'success', 'token_type': 'password', 'messageType': 'error'}
            else:
                tokenCreateTime = filterTime.strftime("%Y-%m-%d %H:%M:%S")
                currentTime = dt.now().strftime("%Y-%m-%d %H:%M:%S")

                fmt = '%Y-%m-%d %H:%M:%S'
                tokenCreateTimeNew = dt.strptime(tokenCreateTime, fmt)
                currentTimeNew = dt.strptime(currentTime, fmt)

                minutesDifference = currentTimeNew - tokenCreateTimeNew
                diff_minutes = (minutesDifference.days * 24 *
                                60) + (minutesDifference.seconds / 60)

                if diff_minutes >= 2880:
                    messageData = {'message': 'Your token is expired. Please try again.',
                                   'responseType': 'success', 'token_type': 'password', 'messageType': 'error'}
                else:
                    messageData = {'message': 'Your toke to reset password is valid.', 'responseType': 'success',
                                   'token_type': 'password', 'messageType': 'success', 'email': filterData.user_email}
                # return HttpResponse(json.dumps(messageData))
                context = {}
                context['messageData'] = messageData
                return render(request, 'resetpassword.html', context)
                # form = ResetPassword()
                # return render(request, 'resetpassword.html',
                #                   {'form': form})
    except Exception as e:
        print('error is ', e)


'''
def forgotPassword(request):
    errormail = False
    usernotexist = False
    res = 0
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email','')
            # print(email)
            try :
                u = User.objects.get(email=email)
            except :
                return redirect('/live/forgot_password?usernotexist=True')
            if  u :
                try:
                    res = send_mail('Change your password', 'http://127.0.0.1:8000/live/reset_password/?token='+get_sec_code() + '\n\n\n' + 'change your password within 5 minutes !!!', 'tickets@ercess.com', [email,])
                    clear_list()
                except Exception as e:
                    print(res)
                    print(e)
                    pass
                if res  == 1:
                    # give submission message to user
                    return redirect('/live/login?mail=True')
                else :
                    # give error to user
                    return redirect('/live/forgot_password?errormail=True')

            else :
                #raise user doesnot exist
                return redirect('/live/forgot_password?usernotexist=True')
        form = ForgotPasswordForm()
        return render(request, 'fogotpassword.html', {'form': form})
    else:
        form = ForgotPasswordForm()
        if 'errormail' in request.GET:
            errormail = True
        if 'usernotexist' in request.GET:
            usernotexist = True
        return render(request, 'fogotpassword.html', {'form': form ,'errormail':errormail ,'usernotexist':usernotexist})

def resetPassword(request):
    usernotexist = False
    passnotmatch = False
    if request.method == 'POST':
        form = ResetPassword(request.POST)
        if form.is_valid():
            email = request.POST.get('email', '')
            password = request.POST.get('password','')
            rpassword = request.POST.get('rpassword', '')
            try:
                u = User.objects.get(email=email)
            except :
                return redirect('/live/reset_password?usernotexist=True')
            if  u :
                if password == rpassword :
                    u.set_password(password)
                    u.save()
                    return redirect('/live/login?passchange=True')
                else :
                    #raiseerror password not matching
                    return redirect('/live/reset_password?passnotmatch=True')
            else :
                #raise user does not exist
                return redirect('/live/reset_password?usernotexist=True')
        form = ResetPassword()
        return render(request, 'resetpassword.html', {'form': form})
    else:
        form = ResetPassword()

        if 'usernotexist' in request.GET:
            usernotexist = True
        if 'passnotmatch' in request.GET:
            passnotmatch = True
        if 'token' in request.GET:
            token = request.GET.get('token', '')
            res = check_token(token)
            print(res)
            if res == 1 :
                return render(request, 'resetpassword.html',
                              {'form': form, 'usernotexist': usernotexist, 'passnotmatch': passnotmatch})
            elif res == 0 :
                return render(request , 'request_timeout.html')
        else :
            return render(request, '403.html')
        return render(request, 'resetpassword.html',
                      {'form': form, 'usernotexist': usernotexist, 'passnotmatch': passnotmatch})
'''

SITE_PROTOCOL = 'https://'
def home(request):
    newthing = SITE_PROTOCOL+str(request.get_host())+str(reverse("dashboard:package-payment-success"))
    print(' >', newthing)
    try:

        try:
            print('trying to delete session data',
                  request.session.get('username'))
            del request.session['username']
            request.session.modified = True
        except Exception as e:
            print(e)
        try:
            print('trying to delete session  sub data',
                  request.session.get('sub'))
            del request.session['sub']
            request.session.modified = True
        except Exception as e:
            print(e)
        try:
            logout(request)
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
    return render(request, 'index.html')


def multichannelpromotion(request):
    # print('multichannel promotion')
    return render(request, 'multichannel_promotion.html')

def smsMarketing(request):
    # print('multichannel promotion')
    return render(request, 'sms-marketing.html')

def emailMarketing(request):
    # print('multichannel promotion')
    return render(request, 'email-marketing.html')

def referralProgram(request):
    # print('multichannel promotion')
    return render(request, 'referral-program-details.html')

def strategicContentMarketing(request):
    # print('multichannel promotion')
    return render(request, 'strategic-content-marketing.html')

def startup(request):
    # print('multichannel promotion')
    return render(request, 'startup.html')

def enterprise(request):
    # print('multichannel promotion')
    return render(request, 'enterprise.html')

def musicDance(request):
    # print('multichannel promotion')
    return render(request, 'music-dance.html')

def entertainment(request):
    # print('multichannel promotion')
    return render(request, 'entertainment.html')

def networking(request):
    # print('multichannel promotion')
    return render(request, 'networking.html')

def learning(request):
    # print('multichannel promotion')
    return render(request, 'learning.html')

def faq(request):
    # print('multichannel promotion')
    return render(request, 'faq.html')

def knowledgeBase(request):
    # print('multichannel promotion')
    return render(request, 'knowledge-base.html')

def visionMissionValues(request):
    # print('multichannel promotion')
    return render(request, 'vision-mission-values.html')


def sellstallspaces(request):
    return render(request, 'stall_spaces.html')


def advertisement(request):
    return render(request, 'paid-advertisement.html')


def howitworks(request):
    # print('inside how it works')
    return render(request, 'how-it-works.html')
#
# def createevent(request):
#     pass
#
#
# def manageevents(request):
#     pass
#
#
# def salesreport(request):
#     pass


def aboutus(request):
    return render(request, 'about-us.html')


def contactus(request):
    res = 0
    x = 0
    send_to = 'tickets@ercess.com'
    contactregerror = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name', '')
            email = form.cleaned_data.get('email', '')
            mobile = form.cleaned_data.get('mobile', '')
            purpose = form.cleaned_data.get('purpose', '')
            comment = form.cleaned_data.get('comment', '')
            try:
                res = send_mail('Customer Query', 'contact details of customer' + 'name : ' + name + 'email : ' + email + 'phone no :' + str(mobile)
                                + 'purpose :' + purpose + 'comments :' + comment, email, [email, ])

                con = ContactData(
                    username=name,
                    email=email,
                    mobile=mobile,
                    purpose=purpose,
                    comment=comment
                )

                x = con.save()

            except Exception as e:
                print(e)

            if res == 1 and x is None:
                # give submission message to user
                return redirect('/live/login?contact=True')
            else:
                # give error to user
                return redirect('/live/contact?contactregerror=True')
        form = ForgotPasswordForm()
        return render(request, 'contact-us.html', {'form': form})
    else:
        form = ContactForm()
        if 'contactregerror' in request.GET:
            contactregerror = True
        return render(request, 'contact-us.html', {'form': form, 'contactregerror': contactregerror})


def blog(request):
    data = BlogData.objects.all()
    return render(request, 'blog.html', {'data': data[0], 'desc': data[0].description[0:300]})


def blogpost(request, pk):

    data = BlogData.objects.get(pk=pk)
    return render(request, 'blog-post.html', {'data': data})


def career(request):
    return render(request, 'careers.html')


def pricing(request):
    return render(request, 'pricing.html')


def no_event_page(request):
    return render(request, 'no_event_page.html')


def partners(request):
    return render(request, 'partners.html')


def marketing(request):
    pass


def privacypolicy(request):
    return render(request, 'privacy-policy.html')


def logoutview(request):
    time = timezone.now()
    username = request.session.get('username')
    print(username)

    try:
        if not request.session.get('username'):
            return redirect('/live/')
        # logout(request)
        # print('trying to delete session data', request.session.get('username'))
        if 'admin_id' in request.session.keys():
            action = AdminActionLog()
            action.admin_id = request.session['admin_id']
            print(action.admin_id)
            print("--------------------------------")
            action.timestamp = time
            action.parameter = "log-out"
            action.event_id = 0
            action.action_taken = "logged out"
            action.save()
        print('--------------------')
        for key in list(request.session.keys()):
            del request.session[key]

        #del request.session['username']
        #del request.session['sub']
        #print('data deleted')
        #print('auth logging out')
        # print(request.session.keys())
        # request.session.flush()
        # request.session = {}
        # print(request.session.keys())

        return render(request, 'index.html')

    except:
        print('unable to delete')
        return render(request, 'index.html')


def blogdetails(request):
    blogs = BlogData.objects.all()
    data = {"results": list(blogs.values(
        'blog_id', 'title', 'author', 'date', 'description'))}
    return JsonResponse(data)


def blogspecific(request, pk):
    blog = get_object_or_404(BlogData, pk=pk)
    data = {
        "results": {
            'blog_id': blog.blog_id,
            'title': blog.title,
            'author': blog.author,
            'date': blog.date,
            'description': blog.description
        }
    }
    return JsonResponse(data)


def bad_request(request):
    response = render_to_response('400.html')
    response.status_code = 400
    return response


def permission_denied(request):
    response = render_to_response('403.html')
    response.status_code = 403
    return response


def page_not_found(request):
    response = render_to_response('404.html')
    response.status_code = 404
    return response


def server_error(request):
    response = render_to_response('500.html')
    response.status_code = 500
    return response


def get_sec_code():
    sc = secrets.token_hex(16)
    l.append(sc)
    print(l)
    return sc


def check_token(token):
    flag = 0
    print('token' + token)
    print('list' + str(l))
    for scc in l:
        print(scc)
        if scc == token:
            flag = 1
    if flag == 1:
        return 1
    else:
        return 0


def clear_list():
    timeout = time.time() + 60 * 5
    while True:
        if time.time() > timeout:
            l.clear()
            break


def manageevents(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    e = []
    r = request.session.get('userid')
    print(r)
    l = StatusPromotionTicketing.objects.all().filter(
        connected_user=r, complete_details=1).values('event_id').order_by('-event_id')
    d = StatusPromotionTicketing.objects.all().filter(
        connected_user=r, complete_details=0).values('event_id').order_by('-event_id')
    now = datetime.now(tz=timezone.utc)
    print(l, d)
    tot_count = [len(l) + len(d)]
    print(tot_count)
    pr = []
    up = []
    pn = []
    un = []
    psd = []
    usd = []
    u_src = []
    p_src = []
    d_src = []
    event_md5_keys = []
    dr_status_promo_tkt = []
    pc = 0
    uc = 0
    for i in range(0, (len(l))):
        p = Articles2.objects.all().filter(edate__lt=now, id=l[i]['event_id'])
        u = Articles2.objects.all().filter(edate__gt=now, id=l[i]['event_id'])
        if len(p) != 0:
            pr.append(p.values('id')[0]['id'])
            pn.append(p.values('event_name')[0]['event_name'])
            psd.append(p.values('sdate')[0]['sdate'])
            p_src.append(p.values('banner')[0]['banner'])

        elif len(u) != 0:
            up.append(u.values('id')[0]['id'])
            un.append(u.values('event_name')[0]['event_name'])
            usd.append(u.values('sdate')[0]['sdate'])
            u_src.append(u.values('banner')[0]['banner'])
    stat = []
    for i in up:
        # print(i)
        st = StatusPromotionTicketing.objects.all().filter(event_id=i)
        # print(st)
        if len(st) != 0:
            stat.append(st.values('event_active')[0]['event_active'])
    print(up)
    print(stat)

    # admin_mobile
    admin_mobile = []
    print("--------admin mobile section -------------------")
    for i in range(0, len(up)):
        # print("---------")
        # print(stat)
        # print(up[i])
        if stat[i] == 5:
            # @author Shubham
            a_m = AdminEventAssignment.objects.all().filter(event_id=up[i])
            # a_m = Admin_Event_Assignment.objects.all().filter(event_id=up[i])
            # ends here ~ @author Shubham
            # print(a_m)
            if len(a_m) != 0:
                a_id = (a_m.values('admin_id')[0]['admin_id'])
                print(a_id)
                ad_m = Admin.objects.all().filter(table_id=a_id)
                print(ad_m)
                if len(ad_m) != 0:
                    num = ad_m[0].mobile
                    print(num)
                    if num != None:
                        admin_mobile.append(num)
                    elif num == None:
                        num = '9886188705'
                        admin_mobile.append(num)

                else:
                    admin_mobile.append('9886188705')
                    # print('nested else')
            else:
                admin_mobile.append('9886188705')
                # print("in this")
        elif stat[i] != 5:
            admin_mobile.append('')

    # for i in t_id:
    #     ad_m=Admin.objects.all().filter(table_id=i)
    #     if len(ad_m)!=0:
    #         admin_mobile.append(ad_m.values('mobile')[0]['mobile'])
    #     else:
    #         admin_mobile.append('9886188705')
    print(admin_mobile)
    print("----------admin mobile--------------")
    print('up>>>>>>>>>>>>>>>>>>>>>',up)
    print(un)
    print(usd)
    print(stat)
    print(u_src)

    event_active = []
    if up:
        for j in up:
            event = StatusPromotionTicketing.objects.get(event_id = j)
            active_event = event.event_active
            event_active.append(active_event)

    upcm = itertools.zip_longest(up, un, usd, stat, admin_mobile, u_src,event_active)
#    upcm = zip(up,un,usd,stat,admin_mobile,u_src)
#    print("UPCNM",list(upcm))
    upcm_count = [len(up)]
    # for previous meetings

    # qy=[]
    # qk=[]
    #
    # for k in pr:
    #     q = Tickets_Sale.objects.all().filter(event_id=k).values('table_id')
    #     for h in q:
    #         qy
    #         qk.append(h['table_id'])
    #     qy.append(qk)
    # qty = []
    # qt =[]
    # for i in qy:
    #     for t in i:
    #         qty_l = Tickets_Sale.objects.all().filter(table_id=t).values('qty')
    #         qt.append(qty_l[0]['qty'])
    #     qty.append(qt)
    #
    # val=0
    # value = []
    # for i in qty:
    #     for t in i:
    #         val=val+t
    #     value.append(val)

    print("tickets--------------------------------")
    print(pr)
    event_active = []
    for j in pr:
        event = StatusPromotionTicketing.objects.get(event_id = j)
        active_event = event.event_active
        event_active.append(active_event)

    value = []

    for i in pr:

        # @author Shubham
        tickt = TicketsSale.objects.all().filter(event_id=i)
        # tickt = Tickets_Sale.objects.all().filter(event_id=i)
        # ends here ~ @author Shubham


        if len(tickt) != 0:
            sum = 0
            for i in tickt:
                if (i.qty != None):
                    sum += i.qty
            value.append(sum)
        else:
            value.append(0)

    print(value)

    int_c = []
    for k in pr:


        # @author Shubham
        ct = Rsvp.objects.all().filter(event_id=k).values('table_id').count()
        # ct = Rsvp.objects.all().filter(event_id=k).values('table_id').count()
        # ends here ~ @author Shubham

        int_c.append(ct)

    prev = zip(pr, pn, psd, value, int_c, p_src,event_active)
    prev_count = [len(pr)]

    # draft
    d_id = []
    d_n = []
    d_sd = []
    draft_count = [len(d)]
    # print(d)
    for i in d:
        # print(i)
        dr = Articles2.objects.all().filter(id=i['event_id'])
        dr_status_promo_tkt_filter = StatusPromotionTicketing.objects.all().filter(event_id=i['event_id']).values()
       

        # print(dr)
        if len(dr) != 0:
            d_id.append(dr.values('id')[0]['id'])
            d_n.append(dr.values('event_name')[0]['event_name'])
            d_sd.append(dr.values('sdate')[0]['sdate'])
            d_src.append(dr.values('banner')[0]['banner'])
            event_md5_keys.append(md5(dr.values('event_name')[0]['event_name'].encode('utf-8')).hexdigest()[:34])
            dr_status_promo_tkt.append(list(dr_status_promo_tkt_filter)[0])

            event_active = []
            for j in d_id:
                event = StatusPromotionTicketing.objects.get(event_id = j)
                active_event = event.event_active
                event_active.append(active_event)

    # print(d_id)
    draft = zip(d_id, d_n, d_sd, d_src, event_md5_keys, dr_status_promo_tkt,event_active)
    print(tot_count, upcm_count, prev_count, draft_count)
    count = zip(tot_count, upcm_count, prev_count, draft_count)

    return render(request, 'dashboard/organizer_dashboard.html', {'prev': prev, 'upcm': upcm, 'draft': draft, 'count': count})


def RSVP(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    user = request.session.get('userid')
    print(user)

    ticketing = StatusPromotionTicketing.objects.all().filter(connected_user=user, complete_details=1).exclude().values('event_id').order_by('event_id')
    print(ticketing)
    count_t = len(ticketing)
    now = datetime.now()

    # upcoming tab
    up_id = []
    up_sdate = []
    up_name = []
    up_ban = []
    up_city = []
    up_message = []

    # past_tab
    pa_id = []
    pa_sdate = []
    pa_name = []
    pa_ban = []
    pa_city = []
    pa_message = []

    for i in range(0, count_t):
        up_eve = Articles2.objects.filter(sdate__gt=now, id=ticketing[i]['event_id']).all() | Articles2.objects.filter(
            edate__gt=now, id=ticketing[i]['event_id']).all()

        pa_eve = Articles2.objects.filter(
            edate__lt=now, id=ticketing[i]['event_id']).all()

        if len(up_eve) != 0:
            up_id.append(up_eve.values('id')[0]['id'])
            up_sdate.append(up_eve.values('sdate')[0]['sdate'])
            up_name.append(up_eve.values('event_name')[0]['event_name'])
            up_ban.append(up_eve.values('banner')[0]['banner'])
            up_city.append(up_eve.values('city')[0]['city'])

        elif len(pa_eve) != 0:
            pa_id.append(pa_eve.values('id')[0]['id'])
            pa_sdate.append(pa_eve.values('sdate')[0]['sdate'])
            pa_name.append(pa_eve.values('event_name')[0]['event_name'])
            pa_ban.append(pa_eve.values('banner')[0]['banner'])
            pa_city.append(pa_eve.values('city')[0]['city'])
    # RSVP count for upcoming tab
    print(up_id)
    up_count = []
    for i in up_id:
        rsv = Rsvp.objects.all().filter(event_id=i)
        print(rsv)
        if len(rsv) != 0:
            count = 0
            for i in rsv:
                count += 1
            up_count.append(count)
        elif len(rsv) == 0:
            up_count.append(0)
    print(up_count)

    # RSVP count for past tab
    print(pa_id)
    pa_count = []
    for i in pa_id:
        rsv = Rsvp.objects.all().filter(event_id=i)
        print(rsv)
        if len(rsv) != 0:
            count = 0
            for i in rsv:
                count += 1
            pa_count.append(count)
        elif len(rsv) == 0:
            pa_count.append(0)
    print(pa_count)

    upcoming = zip(up_id, up_name, up_sdate, up_ban, up_city, up_count)
    u_cnt = len(up_id)
    past = zip(pa_id, pa_name, pa_sdate, pa_ban, pa_city, pa_count)
    p_cnt = len(pa_id)

    return render(request, 'dashboard/RSVP.html', {'upcoming': upcoming, 'u_cnt': u_cnt, 'p_cnt': p_cnt,
                                                   'past': past, 't_count': count_t})


def getInquiries(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    return render(request, 'dashboard/inquiries.html')


def getSales(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    user = request.session.get('userid')

    ticketing = StatusPromotionTicketing.objects.all().filter(connected_user=user,
                                                              complete_details=1).exclude().values('event_id').order_by('-event_id')
    print(ticketing)
    count_t = len(ticketing)
    now = datetime.now()

    # upcoming tab
    up_id = []
    up_sdate = []
    up_name = []
    up_ban = []
    up_city = []

    # past_tab
    pa_id = []
    pa_sdate = []
    pa_name = []
    pa_ban = []
    pa_city = []

    for i in range(0, count_t):
        up_eve = Articles2.objects.filter(sdate__gt=now, id=ticketing[i]['event_id']).all() | Articles2.objects.filter(
            edate__gt=now, id=ticketing[i]['event_id']).all()

        pa_eve = Articles2.objects.filter(
            edate__lt=now, id=ticketing[i]['event_id']).all()

        if len(up_eve) != 0:
            up_id.append(up_eve.values('id')[0]['id'])
            up_sdate.append(up_eve.values('sdate')[0]['sdate'])
            up_name.append(up_eve.values('event_name')[0]['event_name'])
            up_ban.append(up_eve.values('banner')[0]['banner'])
            up_city.append(up_eve.values('city')[0]['city'])

        elif len(pa_eve) != 0:
            pa_id.append(pa_eve.values('id')[0]['id'])
            pa_sdate.append(pa_eve.values('sdate')[0]['sdate'])
            pa_name.append(pa_eve.values('event_name')[0]['event_name'])
            pa_ban.append(pa_eve.values('banner')[0]['banner'])
            pa_city.append(pa_eve.values('city')[0]['city'])

    # count of ticket sale upcoming events
    up_sale = []

    print(up_id)
    for i in up_id:

        # @author Shubham
        sale = TicketsSale.objects.all().filter(event_id=i).values('qty')
        #  sale = Tickets_Sale.objects.all().filter(event_id=i).values('qty')
        # ends here ~ @author Shubham

        u_s = 0
        print(sale)

        if len(sale) != 0:
            for i in sale:
                print(i)
                qty = i['qty']
                u_s += qty
            up_sale.append(u_s)
        elif len(sale) == 0:
            up_sale.append(0)
    print(up_sale)

    # count of ticket sale past events
    pa_sale = []

    for i in pa_id:

        # @author Shubham
        sale = TicketsSale.objects.all().filter(event_id=i).values('qty')
        # sale = Tickets_Sale.objects.all().filter(event_id=i).values('qty')
        # ends here ~ @author Shubham
        p_s = 0

        if len(sale) != 0:
            for i in sale:
                qty = i['qty']
                p_s += qty
            pa_sale.append(p_s)
        elif len(sale) == 0:
            pa_sale.append(0)
    print(pa_sale)

    upcoming = zip(up_id, up_name, up_sdate, up_ban, up_city, up_sale)
    up_count = len(up_id)

    past = zip(pa_id, pa_name, pa_sdate, pa_ban, pa_city, pa_sale)
    pa_count = len(pa_id)

    total_count = up_count + pa_count

    return render(request, 'dashboard/sales.html', {'upcoming': upcoming, 'up_count': up_count,
                                                    'past': past, 'pa_count': pa_count,
                                                    't_count': total_count})


def getHelp(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    return render(request, 'dashboard/help.html')


def profile(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    user = Users.objects.get(pk=request.session['userid'])
    print(user)
    # print(id)
    # user = Users.objects.all().filter(id = id)
    # print(user)
    # , {'user_info': user}
    return render(request, 'dashboard/profile.html', {'user': user})


def settings(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    return render(request, 'dashboard/conf_settings.html')


def rsvp_event(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    rsv = Rsvp.objects.all().filter(event_id=event_id).order_by('-event_id')
    count = len(rsv)
    print('count', count)
    name = []
    email = []
    mobile = []
    recieved = []
    locked_status = []
    tableId = []

    if count != 0:
        for i in rsv:
            name.append(i.attendee_name)
            email.append(i.attendee_email)
            mobile.append(i.attendee_contact)
            recieved.append(i.date_added)
            # @author Shubham ~ October 11 2019
            locked_status.append(i.locked)
            tableId.append(i.table_id)
            # ends here ~ @author Shubham ~ October 11 2019

    event = Articles2.objects.all().filter(id=event_id)
    eventname = ''

    for i in event:
        eventname = i.event_name
    print(eventname)

    items = zip(name, email, mobile, recieved, locked_status, tableId)
    return render(request, 'dashboard/rsvp_event.html', {'count': count, 'items': items, 'eventname': eventname, 'eventId':event_id})


def event_details(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    data = []
    e = Articles2.objects.all().filter(id=event_id)
    eve_id = e.values('id')[0]['id']
    name = [e.values('event_name')[0]['event_name']]

    img = [e.values('banner')[0]['banner']]
    create_date = e.values('date_added')[0]['date_added']

    # for complete details check
    print(e.values('id')[0]['id'])
    status_check = StatusPromotionTicketing.objects.filter(
        event_id=e.values('id')[0]['id']).values('complete_details')
    # print(status_check)
    print(status_check[0]['complete_details'])
    status = False
    if status_check[0]['complete_details'] == 1:
        status = True


    #############################    ADMIN RELATION WITH THE EVENT   ###########################################
    print("admin------------------------ event---------------------assgnmnt")
    assigned = AdminEventAssignment.objects.all().filter(event_id=eve_id)
    print(assigned)

    if assigned:
        admin = Admin.objects.all().filter(table_id=assigned[0].admin_id)
        admin_name = admin[0].fname + " " + admin[0].lname
        print(admin_name)
        contact = admin[0].mobile
        print(contact)
    else:
        admin_name = ''
        contact = ''

    # for sale
    name_s = []
    amt = []
    qty = []


    # @author Shubham
    e_s = TicketsSale.objects.all().filter(event_id=event_id).order_by('-purchase_date').values('table_id')
    # e_s = Tickets_Sale.objects.all().filter(event_id=event_id).order_by('-purchase_date').values('table_id')
    # ends here ~ @author Shubham

    c_s = [len(e_s)]

    for i in range(0, len(e_s)):

        if i < 3:

            # @author Shubham
            d = TicketsSale.objects.all().filter(table_id=e_s[i]['table_id'])
            # d = Tickets_Sale.objects.all().filter(table_id=e_s[i]['table_id'])
            # ends here ~ @author Shubham
            name.append(d.values('attendee_name')[0]['attendee_name'])
            amt.append(d.values('ampunt_paid')[0]['ampunt_paid'])
            qty.append(d.values('qty')[0]['qty'])

    sale = zip(name, amt, qty)

    # for rsvp
    name_r = []
    cont = []
    email = []


    # @author Shubham
    e_r = Rsvp.objects.all().filter(event_id=event_id).order_by('-date_added').values('table_id')
    # e_r = Rsvp.objects.all().filter(event_id=event_id).order_by('-date_added').values('table_id')
    # ends here ~ @author Shubham

    for i in range(0, len(e_r)):
        if i < 3:


            # @author Shubham
            d = Rsvp.objects.all().filter(table_id=e_r[i]['table_id'])
            # d = Rsvp.objects.all().filter(table_id=e_r[i]['table_id'])
            # ends here ~ @author Shubham

            name_r.append(d.values('attendee_name')[0]['attendee_name'])
            cont.append(d.values('attendee_contact')[0]['attendee_contact'])
            email.append(d.values('attendee_email')[0]['attendee_email'])

    rsvp_d = zip(name_r, cont, email)
    c_r = [len(e_r)]

    data = zip(name, img, c_s, c_r)

    # for fail errors
    print("Fail errors---------------------------")
    veri_res = EventVerificationResult.objects.all().filter(event_id=event_id)
    print(veri_res.values('event_id'))
    veri_id = []
    if len(veri_res) != 0:
        for i in veri_res:
            if i.status == 'fail':
                veri_id.append(i.verified_against)
    veri_count = len(veri_id)
    print(veri_id)
    msg_to_org = []
    for i in veri_id:
        process = EventProcesses.objects.all().filter(process_id=i)
        msg_to_org.append(process[0].msg_to_org)

    print(msg_to_org)
    print("-------------------------fail errors")

    # # for site
    # s_n = []
    # c_l = []
    # c_ps = []
    # c_p = []

    # # s = StatusOnChannel.objects.all().filter(event_id=event_id).values('table_id')
    # s = EventStatusOnChannel.objects.all().filter(event_id=event_id).values('table_id')
    # s_len = len(s)
    # print(s)
    # for i in s:
    #     d = EventStatusOnChannel.objects.all().filter(table_id=i['table_id'])
    #     # d = StatusOnChannel.objects.all().filter(table_id=i['table_id'])
    #     s_i = PartnerSites.objects.all().filter(
    #         table_id=(d.values('site_id')[0]['site_id']))
    #     s_n.append(s_i.values('site_name')[0]['site_name'])
    #     c_l.append(d.values('link')[0]['link'])
    #     c_ps.append(d.values('promotion_status')[0]['promotion_status'])
    #     c_p.append(d.values('partner_status')[0]['partner_status'])

    # print(c_l)

    # print("Link ----------------------------------")
    # print(c_l)
    # site_link = []
    # for i in c_l:
    #     if (i == None or i == '' or i == "None" or i == "none" or i == "NULL"):
    #         site_link.append(0)
    #     else:
    #         site_link.append(i)
    # print(site_link)

    # print("----------------------------------ends link")
    # site = zip(s_n, site_link, c_ps, c_p)
    s_len = 0
    site = []
    status = []
    active_status = StatusPromotionTicketing.objects.get(event_id = event_id)
    a = active_status.event_active
    # for i in active_status:
    #     a = i.event_active
    #     print(a,'=====================================')
    # status.append(a)
    # print(status,'>>>>>>>>>>>>>>>>>>>>>>')
    f_status = zip(status)
    return render(request, 'dashboard/event_details.html', {'data': data, 'sale': sale, 'admin': admin_name,
                                                            'contact': contact, 'create': create_date,
                                                            'rsvp': rsvp_d, 'site': site,
                                                            'status': status, 's_len': s_len,
                                                            'eve_id': eve_id, 'veri_count': veri_count,
                                                            'msg_org': msg_to_org,'a':a})


# ===============================
class UpdateStatus(View):
    def post(self,request,event_id):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        response = {}
        try:
            event_status_id = request.POST.get('select_type')  
            event = StatusPromotionTicketing.objects.filter(event_id = event_id).update(event_active = event_status_id)
            response['status'] = True
            response['message'] = 'Successfully Change Status.'
        except Exception as e:
            print(e)
            response['status'] = False
            response['message'] = 'Status. not change'
        return HttpResponse(json.dumps(response),content_type = 'application/json')





def edit_event(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    s = []
    now = datetime.now()
    d = Articles2.objects.all().filter(id=event_id)
    if len(d) == 0:
        return redirect('/live/dashboard/organizer_dashboard')

    spe = StatusPromotionTicketing.objects.all().filter(
        event_id=event_id).values('approval')

    spea = spe[0]['approval']
    print(spea)
    if spea == 1:
        print("logs will be maintained")
    if d.values('event_name').count() > 0:
        s.append(d.values('event_name')[0]['event_name'])
    if d.values('website').count() > 0:
        s.append(d.values('website')[0]['website'])

    k = d.values('sdate')[0]['sdate']
    sl = now.replace(hour=k.hour, minute=k.minute, second=k.second,
                     microsecond=k.microsecond, year=k.year, month=k.month, day=k.day)
    # sd=datetime.date(k)
    print(sl)
    if k.month < 10:
        if k.day < 10:
            sda = '0' + str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
        else:
            sda = str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
    else:
        if k.day < 10:
            sda = '0' + str(k.day) + '/' + str(k.month) + '/' + str(k.year)
        else:
            sda = str(k.day) + '/' + str(k.month) + '/' + str(k.year)
    s.append(sda)
    s.append(d.values('start_time')[0]['start_time'])
    k1 = d.values('edate')[0]['edate']
    el = now.replace(hour=k1.hour, minute=k1.minute, second=k1.second,
                     microsecond=k1.microsecond, year=k1.year, month=k1.month, day=k1.day)

    # ed=datetime.date(k1)
    # print(ed)
    if k1.month < 10:
        if k1.day < 10:
            eda = '0' + str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
        else:
            eda = str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
    else:
        if k1.day < 10:
            eda = '0' + str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
        else:
            eda = str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
    print(eda)
    s.append(eda)
    s.append(d.values('end_time')[0]['end_time'])
    s.append(d.values('address_line1')[0]['address_line1'])
    s.append(d.values('address_line2')[0]['address_line2'])
    s.append(d.values('city')[0]['city'])
    s.append(d.values('state')[0]['state'])
    s.append(d.values('country')[0]['country'])
    s.append(d.values('pincode')[0]['pincode'])
    s.append(d.values('webinar_link')[0]['webinar_link'])
    try:
        s.append(float(d.values('latitude')[0]['latitude']))
    except:
        pass

    try:
        s.append(float(d.values('longitude')[0]['longitude']))
    except:
        pass

    s.append(d.values('place_id')[0]['place_id'])
    s.append(d.values('full_address')[0]['full_address'])
    # s.append(d.values('venue_not_decided')[0]['venue_not_decided'])
    print(s[1])
    par = ['event_name', 'website', 'sdate', 'start_time', 'eddate', 'end_time', 'address_line1',
           'address_line2','city', 'state', 'country', 'pincode', 'latitude', 'longitude', 'place_id','full_address']

    if request.method == 'POST':
        print(event_id)

        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        print(type(start))
        l = []
        articles2 = Articles2.objects.get(id=event_id)
        print(request.session['userid'])

        event_name = request.POST.get('event_name', '')
        l.append(event_name)
        website = request.POST.get('website', '')
        l.append(website)
        stdate = request.POST.get('sdate', '')
        sdate = now.replace(hour=0, minute=0, second=0, microsecond=0, year=int(
            stdate[6:]), month=int(stdate[3:5]), day=int(stdate[:2]))
        l.append(sdate)
        start_t = request.POST.get('start_time', '')
        print(len(start_t), start_t[6:], start_t[:2])

        if start_t[0] == '1' and start_t[1] != ':':
            if start_t[6:] == 'AM' and start_t[:2] != '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'AM' and start_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                start_time = now.time().replace(hour=0, minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'PM' and start_t[:2] == '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[:2]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
        else:
            if start_t[5:] == 'AM':
                start_time = now.time().replace(hour=int(start_t[0]), minute=int(
                    start_t[2:4]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[0]) + 12), minute=int(start_t[2:4]), second=0, microsecond=0)
        # print(start_time[0],start_time[2:4],start_time[5:])
        # start_time = now.time().replace(hour=int(start_t[0]), minute=int(start_t[2:4]), second=0, microsecond=0)
        # print(datetime.time(int(start_time[0]),int(start_time[2:4]),0))
        print(start_time)
        l.append(start_time)
        eddate = request.POST.get('edate', '')
        edate = now.replace(hour=0, minute=0, second=0, microsecond=0, year=int(
            eddate[6:]), month=int(eddate[3:5]), day=int(eddate[:2]))
        l.append(edate)
        end_t = request.POST.get('end_time', '')
        # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
        print(len(end_t), end_t[6:], end_t[:2])

        if end_t[0] == '1' and end_t[1] != ':':
            if end_t[6:] == 'AM' and end_t[:2] != '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'AM' and end_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                end_time = now.time().replace(hour=0, minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'PM' and end_t[:2] == '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[:2]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
        else:
            if end_t[5:] == 'AM':
                end_time = now.time().replace(hour=int(end_t[0]), minute=int(
                    end_t[2:4]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[0]) + 12), minute=int(end_t[2:4]), second=0, microsecond=0)
        print(end_time)
        l.append(end_time)
        address_line1 = request.POST.get('address_line1', '')
        l.append(address_line1)
        address_line2 = request.POST.get('address_line2', '')
        l.append(address_line2)
        city = request.POST.get('city', '')
        l.append(city)
        state = request.POST.get('state', '')
        l.append(state)
        country = request.POST.get('country', '')
        l.append(country)
        pincode = request.POST.get('pincode', 0)
        latitude = request.POST.get('latitude', '')
        longitude = request.POST.get('longitude', '')
        webinar_link = request.POST.get('webinar_link', '')
        l.append(int(pincode))
        l.append(webinar_link)
        if webinar_link:
            l.append(latitude)
            l.append(longitude)
        else:
            l.append(float(latitude))
            l.append(float(longitude))
        place_id = request.POST.get('place_id', '')
        l.append(place_id)
        full_address = request.POST.get('full_address','')
        l.append(full_address)
        # for venue not started
        venue_not_decided = request.POST.get('venue_not_decided', '')
        if venue_not_decided == 'true':
            venue_not_decided = True
        else:
            venue_not_decided = False


        # ends here ~ for venue not started

        print(stdate, eddate)

        # for i in range(0,len(s)):

        #     print(l[i],s[i])

        print(l[2], str(l[2].day))
        if l[0] != s[0]:
            print("0")
            articles2.event_name = event_name
            print(l[0], s[0])
            if spea == 1:
                log = EventEditLogs(old_data=s[0], new_data=l[0], parameter=par[0], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[1] != s[1]:
            print("1")
            articles2.website = website
            print(l[0], s[0])
            if spea == 1:
                log = EventEditLogs(old_data=s[1], new_data=l[1], parameter=par[1], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[2] != sl:
            print("2")
            articles2.sdate = sdate
            print(l[2], sl)
            if spea == 1:
                log = EventEditLogs(old_data=sl, new_data=l[2], parameter=par[2], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[3] != s[3]:
            print("3")
            articles2.start_time = start_time
            print(l[3], s[3])
            if spea == 1:
                log = EventEditLogs(old_data=s[3], new_data=l[3], parameter=par[3], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[4] != el:
            print("3")
            articles2.edate = edate
            print(l[4], el)
            if spea == 1:
                log = EventEditLogs(old_data=el, new_data=l[4], parameter=par[4], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[5] != s[5]:
            print("5")
            articles2.end_time = end_time
            print(l[5], s[5])
            if spea == 1:
                log = EventEditLogs(old_data=s[5], new_data=l[5], parameter=par[5], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[6] != s[6]:
            print("6")
            articles2.address_line1 = l[6]
            print(l[6], s[6])
            if spea == 1:
                log = EventEditLogs(old_data=s[6], new_data=l[6], parameter=par[6], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[7] != s[7]:
            print("7")
            articles2.address_line2 = address_line2
            print(l[7], s[7])
            if spea == 1:
                log = EventEditLogs(old_data=s[7], new_data=l[7], parameter=par[7], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()


        if l[8] != s[8]:
            print("8")
            articles2.city = city
            print(l[8], s[8])
            if spea == 1:
                log = EventEditLogs(old_data=s[8], new_data=l[8], parameter=par[8], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[9] != s[9]:
            print("8")
            articles2.state = state
            print(l[9], s[9])
            if spea == 1:
                log = EventEditLogs(old_data=s[9], new_data=l[9], parameter=par[9], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[10] != s[10]:
            print("10")
            articles2.country = country
            print(l[10], s[10])
            if spea == 1:
                log = EventEditLogs(old_data=s[10], new_data=l[10], parameter=par[10], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[11] != s[11]:
            print("11")
            articles2.pincode = pincode
            print(l[11], s[11])
            if spea == 1:
                log = EventEditLogs(old_data=s[11], new_data=l[11], parameter=par[11], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[12] != s[12]:
            print("12")
            articles2.webinar_link = webinar_link
            print(l[12], s[12])
            if spea == 1:
                log = EventEditLogs(old_data=s[12], new_data=l[12], parameter=par[12], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[13] != s[13]:
            print("13")
            articles2.latitude = l[13]
            print(l[13], s[13])
            if spea == 1:
                log = EventEditLogs(old_data=s[13], new_data=l[13], parameter=par[13], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l.count(14) > 0 and l[14] != s[14]:
            print("14")
            articles2.longitude = l[14]
            print(l[14], s[14])
            if spea == 1:
                log = EventEditLogs(old_data=s[14], new_data=l[14], parameter=par[14], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l.count(15) > 0 and l[15] != s[15]:
            print("15")
            articles2.place_id = l[15]
            print(l[15], s[15])
            if spea == 1:
                log = EventEditLogs(old_data=s[15], new_data=l[15], parameter=par[15], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l.count(16) > 0 and l[16] != s[16]:
            print("16")
            articles2.full_address = l[16]
            print(l[16], s[16])
            if spea == 1:
                log = EventEditLogs(old_data=s[16], new_data=l[16], parameter=par[16], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()
        
        print(l)

        # articles2.event_name = event_name
        # articles2.sdate = sdate
        # articles2.edate = edateif venue_not_decided == 'true':
        # articles2.start_time = start_time
        # articles2.end_time = end_time
        # articles2.address_line1 = address_line1
        # articles2.address_line2 = address_line2
        # articles2.city = city
        # articles2.state = state
        # articles2.country = country
        # articles2.pincode = pincode
        # articles2.latitude = l[11]
        # articles2.longitude = l[12]
        articles2.venue_not_decided = venue_not_decided
        articles2.save()

        # l[1]=
        # l[3]=

        k_l = l[2]
        if k_l.month < 10:
            if k_l.day < 10:
                print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee", k_l.day)
                l[2] = '0' + str(k_l.day) + '/0' + \
                    str(k_l.month) + '/' + str(k_l.year)
            else:
                l[2] = str(k_l.day) + '/0' + \
                    str(k_l.month) + '/' + str(k_l.year)
        else:
            if k_l.day < 10:
                l[2] = '0' + str(k_l.day) + '/' + \
                    str(k_l.month) + '/' + str(k_l.year)
            else:
                l[2] = str(k_l.day) + '/' + str(k_l.month) + \
                    '/' + str(k_l.year)

        k1_l = l[4]

        if k1_l.month < 10:
            if k1_l.day < 10:
                l[4] = '0' + str(k1_l.day) + '/0' + \
                    str(k1_l.month) + '/' + str(k1_l.year)
            else:
                l[4] = str(k1_l.day) + '/0' + \
                    str(k1_l.month) + '/' + str(k1_l.year)
        else:
            if k1_l.day < 10:
                l[4] = '0' + str(k1_l.day) + '/' + \
                    str(k1_l.month) + '/' + str(k1_l.year)
            else:
                l[4] = str(k1_l.day) + '/' + str(k1_l.month) + \
                    '/' + str(k1_l.year)

        print(l, s)
        print(l[2], s[2])
        print(l[4], s[4])

        return render(request, 'dashboard/edit_event.html', {'event_id': event_id, 's': l, })

    return render(request, 'dashboard/edit_event.html', {'event_id': event_id, 's': s, })



# def edit_action_one(request, event_id):

#     print(event_id)
#     now = datetime.now()
#     start = now.replace(hour=0, minute=0, second=0, microsecond=0)
#     print(type(start))
#     articles2 = Articles2.objects.get(id = event_id)
#     event_name=request.POST.get('event_name','')
#     stdate=request.POST.get('sdate','')
#     start_time=request.POST.get('start_time','')
#     eddate=request.POST.get('edate','')
#     end_time=request.POST.get('end_time','')
#     address_line1=request.POST.get('address_line1','')
#     address_line2=request.POST.get('address_line2','')
#     city=request.POST.get('city','')
#     state=request.POST.get('state','')
#     country=request.POST.get('country','')
#     pincode=request.POST.get('pincode','')
#     latitude=request.POST.get('latitude','')
#     longitude=request.POST.get('longitude','')
#     print(stdate,eddate)

#     sdate=now.replace(hour=0, minute=0, second=0, microsecond=0, year=int(stdate[6:]), month=int(stdate[3:5]), day=int(stdate[:2]))
#     edate=now.replace(hour=0, minute=0, second=0, microsecond=0, year=int(eddate[6:]), month=int(eddate[3:5]), day=int(eddate[:2]))

#     print(sdate,edate)

#     articles2.event_name = event_name
#     articles2.sdate = sdate
#     articles2.edate = edate
#     articles2.start_time = start_time
#     articles2.end_time = end_time
#     articles2.address_line1 = address_line1
#     articles2.address_line2 = address_line2
#     articles2.city = city
#     articles2.state = state
#     articles2.country = country
#     articles2.pincode = pincode
#     articles2.latitude = latitude
#     articles2.longitude = longitude

#     articles2.save()

#     # s_u=Articles2(id=event_id,event_name=event_name,start_time=start_time,end_time=end_time,address_line1=address_line1,address_line2=address_line2,city=city,state=state,country=country)
#     # print(s_u)

#     # s_u.save()

#     #sdate=sdate,start_time=start_time,edate=edate,end_time=end_time,
#     # s=[]
#     # d = Articles2.objects.all().filter(id=event_id)
#     # s.append(d.values('event_name')[0]['event_name'])
#     # s.append(d.values('sdate')[0]['sdate'])
#     # s.append(d.values('start_time')[0]['start_time'])
#     # s.append(d.values('edate')[0]['edate'])
#     # s.append(d.values('end_time')[0]['end_time'])
#     # s.append(d.values('address_line1')[0]['address_line1'])
#     # s.append(d.values('address_line2')[0]['address_line2'])
#     # s.append(d.values('city')[0]['city'])
#     # s.append(d.values('state')[0]['state'])
#     # s.append(d.values('country')[0]['country'])
#     # s.append(d.values('pincode')[0]['pincode'])


#     return HttpResponseRedirect(reverse('dashboard:edit-event-two', args=(event_id,)))

# def edit_event_two(request, event_id):
#     if 'userid' not in request.session.keys():
#         return redirect('/live/login')

#     cat = []
#     cat1 = []
#     a = Categories.objects.all().values('category')
#     # print(a)
#     for i in a:
#         cat.append(i['category'])
#     a1 = Categories.objects.all().values('category_id')
#     # print(a1)
#     for i in a1:
#         cat1.append(i['category_id'])
#     # print(cat1)
#     c = zip(cat, cat1)
#     e = CategorizedEvents.objects.all().filter(
#         event_id=event_id).values('category_id')
#     k = e.values('category_id')[0]['category_id']
#     l = e.values('topic_id')[0]['topic_id']
#     print(type(k), l)

#     a2 = Topics.objects.all().filter(category=k).values('topic')
#     a3 = Topics.objects.all().filter(category=k).values('topics_id')
#     # print(a2,a3)
#     to = []
#     t_i = []
#     for i in range(0, len(a2)):
#         to.append(a2[i]['topic'])
#         t_i.append(a3[i]['topics_id'])
#     print(to, t_i)
#     t = zip(to, t_i)

#     f = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
#     pr = f.values('private')[0]['private']
#     tick = f.values('ticketing')[0]['ticketing']
#     print(type(pr), tick)

#     # if request.method=='POST':
#     #     h=request.POST.get('value','')
#     #     print(h)
#     #     data ={'a2':Topics.objects.all().filter(category=h)}
#     #     a3=Topics.objects.all().filter(category=h).values('topics_id')

#     #     # t=zip(a2,a3)

#     #     return JsonResponse(data)

#     return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 'c': c, 'k': k, 't': t, 'l': l, 'pr': pr, 'tick': tick})


###############

def edit_event_two(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    # cat = []
    # cat1 = []
    # a = Categories.objects.all().values('category')
    # # print(a)
    # for i in a:
    #     cat.append(i['category'])
    # a1 = Categories.objects.all().values('category_id')
    # # print(a1)
    # for i in a1:
    #     cat1.append(i['category_id'])
    # # print(cat1)
    # c = zip(cat, cat1)

    # @author Shubham ~ old code modified on december 27 2019
    cat = []
    cat1 = []
    a = Categories.objects.all().values('category','category_id')
    for i in a:
        cat.append(i['category'])
        cat1.append(i['category_id'])
    c = zip(cat, cat1)
    # # ends here ~ @author Shubham ~ old code modified on december 27 2019

    e = CategorizedEvents.objects.all().filter(
        event_id=event_id).values('category_id')

    k = ''
    l = ''
    if e.values('category_id').count() > 0 and e.values('topic_id').count() > 0:
        k = e.values('category_id')[0]['category_id']
        l = e.values('topic_id')[0]['topic_id']
        print(type(k), l)

    a2 = Topics.objects.all().filter(category=k).values('topic')
    a3 = Topics.objects.all().filter(category=k).values('topics_id')
    # print(a2,a3)
    to = []
    t_i = []
    for i in range(0, len(a2)):
        to.append(a2[i]['topic'])
        t_i.append(a3[i]['topics_id'])
    print(to, t_i)
    t = zip(to, t_i)

    f = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
    pr = f.values('private')[0]['private']
    tick = f.values('ticketing')[0]['ticketing']
    print(type(pr), tick)

    # if request.method=='POST':
    #     h=request.POST.get('value','')
    #     print(h)
    #     data ={'a2':Topics.objects.all().filter(category=h)}
    #     a3=Topics.objects.all().filter(category=h).values('topics_id')

    #     # t=zip(a2,a3)

    #     return JsonResponse(data)

    # get event name from articles 2 table
    articles2Filter = Articles2.objects.get(id=event_id)
    event_name = articles2Filter.event_name
    # ends here ~ get event name from articles 2 table

    return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 'c': c, 'k': k, 't': t, 'l': l, 'pr': pr, 'tick': tick, 'event_name':event_name})


def edit_action_two(request, event_id):
    if request.method == 'GET':

        # cat = []
        # cat1 = []
        # a = Categories.objects.all().values('category')
        # # print(a)
        # for i in a:
        #     cat.append(i['category'])
        # a1 = Categories.objects.all().values('category_id')
        # # print(a1)
        # for i in a1:
        #     cat1.append(i['category_id'])
        # # print(cat1)
        # c = zip(cat, cat1)

        # old code 
        # cat = []
        # cat1 = []
        # a = Categories.objects.all().values('category')
        # # print(a)
        # for i in a:
        #     cat.append(i['category'])
        # a1 = Categories.objects.all().values('category_id')
        # # print(a1)
        # for i in a1:
        #     cat1.append(i['category_id'])
        # # print(cat1)
        # c = zip(cat, cat1)
        # ends here ~ old code

        # @author Shubham ~ old code modified on december 27 2019
        cat = []
        cat1 = []
        a = Categories.objects.all().values('category','category_id')
        for i in a:
            cat.append(i['category'])
            cat1.append(i['category_id'])
        c = zip(cat, cat1)
        # # ends here ~ @author Shubham ~ old code modified on december 27 2019

        # get event name from articles 2 table
        articles2Filter = Articles2.objects.get(id=event_id)
        event_name = articles2Filter.event_name
        # ends here ~ get event name from articles 2 table

        e = CategorizedEvents.objects.all().filter(
            event_id=event_id).values('category_id')
        k = e.values('category_id')[0]['category_id']
        l = e.values('topic_id')[0]['topic_id']
        print(type(k), l)

        a2 = Topics.objects.all().filter(category=k).values('topic')
        a3 = Topics.objects.all().filter(category=k).values('topics_id')
        # print(a2,a3)
        to = []
        t_i = []
        for i in range(0, len(a2)):
            to.append(a2[i]['topic'])
            t_i.append(a3[i]['topics_id'])
        print(to, t_i)
        t = zip(to, t_i)

        f = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
        pr = f.values('private')[0]['private']
        tick = f.values('ticketing')[0]['ticketing']
        print(type(pr), tick)

        # if request.method=='POST':
        #     h=request.POST.get('value','')
        #     print(h)
        #     data ={'a2':Topics.objects.all().filter(category=h)}
        #     a3=Topics.objects.all().filter(category=h).values('topics_id')

        #     # t=zip(a2,a3)

        #     return JsonResponse(data)

        # get event name from articles 2 table
        articles2Filter = Articles2.objects.get(id=event_id)
        event_name = articles2Filter.event_name
        # ends here ~ get event name from articles 2 table

        return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 'c': c, 'k': k, 't': t, 'l': l, 'pr': pr, 'tick': tick, 'event_name':event_name})
    if request.method == 'POST':
        print(event_id)
        now = datetime.now()

        # ca = CategorizedEvents.objects.all().filter(event_id=event_id)
        # sp = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
        ca = CategorizedEvents.objects.get(event_id=event_id)
        sp = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
        # cat = []
        # cat1 = []
        # a = Categories.objects.all().values('category')
        # # print(a)
        # for i in a:
        #     cat.append(i['category'])
        # a1 = Categories.objects.all().values('category_id')
        # # print(a1)
        # for i in a1:
        #     cat1.append(i['category_id'])
        # # print(cat1)
        # c = zip(cat, cat1)

        # @author Shubham ~ old code modified on december 27 2019
        cat = []
        cat1 = []
        a = Categories.objects.all().values('category','category_id')
        # print(a)
        for i in a:
            cat.append(i['category'])
            cat1.append(i['category_id'])
        c = zip(cat, cat1)
        # # ends here ~ @author Shubham ~ old code modified on december 27 2019

        # get event name from articles 2 table
        articles2Filter = Articles2.objects.get(id=event_id)
        event_name = articles2Filter.event_name
        # ends here ~ get event name from articles 2 table

        spe = StatusPromotionTicketing.objects.all().filter(
            event_id=event_id).values('approval')
        spea = spe[0]['approval']
        print(spea)
        if spea == 1:
            print("logs will be maintained")

        e = CategorizedEvents.objects.all().filter(event_id=event_id)
        k1 = e.values('category_id')[0]['category_id']
        l1 = e.values('topic_id')[0]['topic_id']

        f = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
        pr = f.values('private')[0]['private']
        tick = f.values('ticketing')[0]['ticketing']
        print(type(pr), tick)

        cat_id = request.POST.get('category_id', '0')
        top_id = request.POST.get('topic_id', '0')
        pri = request.POST.get('type1', '')
        ticket = request.POST.get('type2', '')

        par = ['category_id', 'topic_id', 'private', 'ticketing']

        if pri == 'public':
            private = 0
        else:
            private = 1
        if ticket == 'paid':
            ticketing = 1
        else:
            ticketing = 0

        print(type(cat_id), top_id, type(private), ticketing)

        if int(cat_id) != k1 and int(top_id) == l1:

            print('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA')

            # h=request.POST.get('category_id','0')
            # print(type(h))
            # a2 = Topics.objects.all().filter(category=cat_id).values('topic')
            # a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
            # # print(a2,type(a3[0]['topics_id']))
            # to = []
            # t_i = []
            # for i in range(0, len(a2)):
            #     to.append(a2[i]['topic'])
            #     t_i.append(a3[i]['topics_id'])
            # print(to, t_i)
            # t = zip(to, t_i)

            # modified code
            a2 = Topics.objects.all().filter(category=cat_id).values('topic','topics_id')
            # print(a2,type(a3[0]['topics_id']))
            to = []
            t_i = []
            for i in range(0, len(a2)):
                to.append(a2[i]['topic'])
                t_i.append(a2[i]['topics_id'])
            print(to, t_i)
            t = zip(to, t_i)
            # ends here ~ modified code

            k = int(cat_id)

            if pr != private:
                print("private")
                sp.private = private
                if spea == 1:
                    log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
                                        event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                    log.save()

            if tick != ticketing:
                print("ticket")
                sp.ticketing = ticketing
                if spea == 1:
                    log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
                                        event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')

                    log.save()
                StatusPromotionTicketing.objects.filter(event_id=event_id).update(private=private,ticketing=ticketing)
            for object in sp:
                object.save()

            pr = private
            tick = ticketing

            return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'pr': pr, 'tick': tick, 'event_name':event_name})

        if int(cat_id) != k1 and int(top_id) != l1:
            print('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')
            # h=request.POST.get('category_id','0')
            # print(type(h))
            # a2 = Topics.objects.all().filter(category=cat_id).values('topic')
            # a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
            # # print(a2,type(a3[0]['topics_id']))
            # to = []
            # t_i = []
            # for i in range(0, len(a2)):
            #     to.append(a2[i]['topic'])
            #     t_i.append(a3[i]['topics_id'])
            # print(to, t_i)
            # t = zip(to, t_i)

            # modified code
            a2 = Topics.objects.all().filter(category=cat_id).values('topic','topics_id')
            # print(a2,type(a3[0]['topics_id']))
            to = []
            t_i = []
            for i in range(0, len(a2)):
                to.append(a2[i]['topic'])
                t_i.append(a2[i]['topics_id'])
            print(to, t_i)
            t = zip(to, t_i)
            # ends here ~ modified code

            k = int(cat_id)
            l = int(top_id)

            for i in t_i:
                if i == int(top_id):
                    if k1 != k:
                        print("Catogory")
                        ca.category_id = cat_id
                        if spea == 1:
                            log = EventEditLogs(old_data=k1, new_data=k, parameter=par[0], taken_action='update',
                                                event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                            log.save()

                    if l1 != l:
                        print("Topic")
                        ca.topic_id = top_id
                        if spea == 1:
                            log = EventEditLogs(old_data=l1, new_data=l, parameter=par[1], taken_action='update',
                                                event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                            log.save()

                        ca.save()

                    if pr != private:
                        print("private")
                        sp.private = private
                        if spea == 1:
                            log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
                                                event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                            log.save()

                    if tick != ticketing:
                        print("ticket")
                        sp.ticketing = ticketing
                        if spea == 1:
                            log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
                                                event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                            log.save()
                        StatusPromotionTicketing.objects.filter(event_id=event_id).update(private=private,ticketing=ticketing)

                    for object in sp:
                        object.save()

            pr = private
            tick = ticketing


            print('event_id', event_id, 't', t, 'c', c, 'k', k, 'l', l, 'pr', pr, 'tick', tick)

            return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'l': l, 'pr': pr, 'tick': tick, 'event_name':event_name})

        if int(cat_id) == k1 and int(top_id) == l1:
            print('CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC')
            # h=request.POST.get('category_id','')
            # print(type(h))
            # a2 = Topics.objects.all().filter(category=cat_id).values('topic')
            # a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
            # # print(a2,type(a3[0]['topics_id']))
            # to = []
            # t_i = []
            # for i in range(0, len(a2)):
            #     to.append(a2[i]['topic'])
            #     t_i.append(a3[i]['topics_id'])
            # print(to, t_i)
            # t = zip(to, t_i)
            k = int(cat_id)
            l = int(top_id)

            # modified code
            a2 = Topics.objects.all().filter(category=cat_id).values('topic','topics_id')
            # print(a2,type(a3[0]['topics_id']))
            to = []
            t_i = []
            for i in range(0, len(a2)):
                to.append(a2[i]['topic'])
                t_i.append(a2[i]['topics_id'])
            print(to, t_i)
            t = zip(to, t_i)
            # ends here ~ modified code

            if pr != private:
                print("private")
                sp.private = private
                if spea == 1:
                    log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
                                        event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                    log.save()

            if tick != ticketing:
                print("ticket")
                sp.ticketing = ticketing
                if spea == 1:
                    log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
                                        event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                    log.save()
                StatusPromotionTicketing.objects.filter(event_id=event_id).update(private=private,ticketing=ticketing)

            for object in sp:
                object.save()

            pr = private
            tick = ticketing

            return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'l': l, 'pr': pr, 'tick': tick, 'event_name':event_name})

        if int(cat_id) == k1 and int(top_id) != l1:
            print('DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD')
            # h=request.POST.get('category_id','')
            # print(type(h))
            # a2 = Topics.objects.all().filter(category=cat_id).values('topic')
            # a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
            # # print(a2,type(a3[0]['topics_id']))
            # to = []
            # t_i = []
            # for i in range(0, len(a2)):
            #     to.append(a2[i]['topic'])
            #     t_i.append(a3[i]['topics_id'])
            # print(to, t_i)
            # t = zip(to, t_i)

            # modified code
            a2 = Topics.objects.all().filter(category=cat_id).values('topic','topics_id')
            # print(a2,type(a3[0]['topics_id']))
            to = []
            t_i = []
            for i in range(0, len(a2)):
                to.append(a2[i]['topic'])
                t_i.append(a2[i]['topics_id'])
            print(to, t_i)
            t = zip(to, t_i)
            # ends here ~ modified code

            k = int(cat_id)
            l = int(top_id)

            for i in t_i:
                if i == int(top_id):
                    print("topic")
                    ca.topic_id = top_id
                    ca.save()
                    if spea == 1:
                        log = EventEditLogs(old_data=l1, new_data=l, parameter=par[1], taken_action='update',
                                            event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                        log.save()
                    if pr != private:
                        print("private")
                        sp.private = private
                        if spea == 1:
                            log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
                                                event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                            log.save()

                    if tick != ticketing:
                        print("ticket")
                        sp.ticketing = ticketing
                        if spea == 1:
                            log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
                                                event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                            log.save()
                        StatusPromotionTicketing.objects.filter(event_id=event_id).update(private=private,ticketing=ticketing)

                    for object in sp:
                        object.save()

            pr = private
            tick = ticketing

            return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'l': l, 'pr': pr, 'tick': tick, 'event_name':event_name})

    return HttpResponseRedirect(reverse('dashboard:edit-event-four', args=(event_id,)))



##############


# def edit_action_two(request, event_id):

#     print(event_id)
#     now = datetime.now()

#     ca = CategorizedEvents.objects.all().filter(event_id=event_id)
#     sp = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
#     cat = []
#     cat1 = []
#     a = Categories.objects.all().values('category')
#     # print(a)
#     for i in a:
#         cat.append(i['category'])
#     a1 = Categories.objects.all().values('category_id')
#     # print(a1)
#     for i in a1:
#         cat1.append(i['category_id'])
#     # print(cat1)
#     c = zip(cat, cat1)

#     spe = StatusPromotionTicketing.objects.all().filter(
#         event_id=event_id).values('approval')
#     spea = spe[0]['approval']
#     print(spea)
#     if spea == 1:
#         print("logs will be maintained")

#     e = CategorizedEvents.objects.all().filter(event_id=event_id)
#     k1 = e.values('category_id')[0]['category_id']
#     l1 = e.values('topic_id')[0]['topic_id']

#     f = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
#     pr = f.values('private')[0]['private']
#     tick = f.values('ticketing')[0]['ticketing']
#     print(type(pr), tick)

#     cat_id = request.POST.get('category_id', '0')
#     top_id = request.POST.get('topic_id', '0')
#     pri = request.POST.get('type1', '')
#     ticket = request.POST.get('type2', '')

#     par = ['category_id', 'topic_id', 'private', 'ticketing']

#     if pri == 'public':
#         private = 0
#     else:
#         private = 1
#     if ticket == 'paid':
#         ticketing = 1
#     else:
#         ticketing = 0

#     print(type(cat_id), top_id, type(private), ticketing)

#     if int(cat_id) != k1 and int(top_id) == l1:
#         # h=request.POST.get('category_id','0')
#         # print(type(h))
#         a2 = Topics.objects.all().filter(category=cat_id).values('topic')
#         a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
#         # print(a2,type(a3[0]['topics_id']))
#         to = []
#         t_i = []
#         for i in range(0, len(a2)):
#             to.append(a2[i]['topic'])
#             t_i.append(a3[i]['topics_id'])
#         print(to, t_i)
#         t = zip(to, t_i)
#         k = int(cat_id)

#         if pr != private:
#             print("private")
#             sp.private = private
#             if spea == 1:
#                 log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
#                                     event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                 log.save()

#         if tick != ticketing:
#             print("ticket")
#             sp.ticketing = ticketing
#             if spea == 1:
#                 log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
#                                     event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                 log.save()
#         for object in sp:
#             object.save()

#         pr = private
#         tick = ticketing

#         return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'pr': pr, 'tick': tick})

#     if int(cat_id) != k1 and int(top_id) != l1:
#         # h=request.POST.get('category_id','0')
#         # print(type(h))
#         a2 = Topics.objects.all().filter(category=cat_id).values('topic')
#         a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
#         # print(a2,type(a3[0]['topics_id']))
#         to = []
#         t_i = []
#         for i in range(0, len(a2)):
#             to.append(a2[i]['topic'])
#             t_i.append(a3[i]['topics_id'])
#         print(to, t_i)
#         t = zip(to, t_i)
#         k = int(cat_id)
#         l = int(top_id)

#         for i in t_i:
#             if i == int(top_id):
#                 if k1 != k:
#                     print("Catogory")
#                     ca.category_id = cat_id
#                     if spea == 1:
#                         log = EventEditLogs(old_data=k1, new_data=k, parameter=par[0], taken_action='update',
#                                             event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                         log.save()

#                 if l1 != l:
#                     print("Topic")
#                     ca.topic_id = top_id
#                     if spea == 1:
#                         log = EventEditLogs(old_data=l1, new_data=l, parameter=par[1], taken_action='update',
#                                             event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                         log.save()

#                 ca.save()

#                 if pr != private:
#                     print("private")
#                     sp.private = private
#                     if spea == 1:
#                         log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
#                                             event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                         log.save()

#                 if tick != ticketing:
#                     print("ticket")
#                     sp.ticketing = ticketing
#                     if spea == 1:
#                         log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
#                                             event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                         log.save()

#                 for object in sp:
#                     object.save()

#         pr = private
#         tick = ticketing

#         return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'l': l, 'pr': pr, 'tick': tick})

#     if int(cat_id) == k1 and int(top_id) == l1:
#         # h=request.POST.get('category_id','')
#         # print(type(h))
#         a2 = Topics.objects.all().filter(category=cat_id).values('topic')
#         a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
#         # print(a2,type(a3[0]['topics_id']))
#         to = []
#         t_i = []
#         for i in range(0, len(a2)):
#             to.append(a2[i]['topic'])
#             t_i.append(a3[i]['topics_id'])
#         print(to, t_i)
#         t = zip(to, t_i)
#         k = int(cat_id)
#         l = int(top_id)

#         if pr != private:
#             print("private")
#             sp.private = private
#             if spea == 1:
#                 log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
#                                     event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                 log.save()

#         if tick != ticketing:
#             print("ticket")
#             sp.ticketing = ticketing
#             if spea == 1:
#                 log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
#                                     event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                 log.save()

#         for object in sp:
#             object.save()

#         pr = private
#         tick = ticketing

#         return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'l': l, 'pr': pr, 'tick': tick})

#     if int(cat_id) == k1 and int(top_id) != l1:
#         # h=request.POST.get('category_id','')
#         # print(type(h))
#         a2 = Topics.objects.all().filter(category=cat_id).values('topic')
#         a3 = Topics.objects.all().filter(category=cat_id).values('topics_id')
#         # print(a2,type(a3[0]['topics_id']))
#         to = []
#         t_i = []
#         for i in range(0, len(a2)):
#             to.append(a2[i]['topic'])
#             t_i.append(a3[i]['topics_id'])
#         print(to, t_i)
#         t = zip(to, t_i)
#         k = int(cat_id)
#         l = int(top_id)

#         for i in t_i:
#             if i == int(top_id):
#                 print("topic")
#                 ca.topic_id = top_id
#                 ca.save()
#                 if spea == 1:
#                     log = EventEditLogs(old_data=l1, new_data=l, parameter=par[1], taken_action='update',
#                                         event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                     log.save()
#                 if pr != private:
#                     print("private")
#                     sp.private = private
#                     if spea == 1:
#                         log = EventEditLogs(old_data=pr, new_data=private, parameter=par[2], taken_action='update',
#                                             event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                         log.save()

#                 if tick != ticketing:
#                     print("ticket")
#                     sp.ticketing = ticketing
#                     if spea == 1:
#                         log = EventEditLogs(old_data=tick, new_data=ticketing, parameter=par[3], taken_action='update',
#                                             event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
#                         log.save()

#                 for object in sp:
#                     object.save()

#         pr = private
#         tick = ticketing

#         return render(request, 'dashboard/edit_event_two.html', {'event_id': event_id, 't': t, 'c': c, 'k': k, 'l': l, 'pr': pr, 'tick': tick})

#     return HttpResponseRedirect(reverse('dashboard:edit-event-four', args=(event_id,)))


# def edit_event_three(request, event_id):
#     if 'userid' not in request.session.keys():
#         return redirect('/live/login')

#     return render(request, 'dashboard/edit_event_four.html', {'event_id': event_id, })


def edit_event_four(request, event_id):
    try:
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        now = datetime.now()
        descform = Articles2Form()

        # print('descform > ', descform)

        a = Articles2.objects.all().filter(id=event_id).values('description','event_name')
        
        event_name = a[0]['event_name']
        d = a[0]['description']

        # d = d[3:]
        # d = d[:-4]
        # d = unescape(d)
        # print(d)
        inst = get_object_or_404(Articles2, id=event_id)
        # print(inst.country)
        qs_india = get_object_or_404(AboutCountries, country="India")
        # print(qs_india.bank_regex1)
        # print(qs_india.bank_regex2)
        bank_regex1 = qs_india.bank_regex1
        bank_regex2 = qs_india.bank_regex2
        # print(type(bank_regex1), type(bank_regex2))

        spe = StatusPromotionTicketing.objects.all().filter(
            event_id=event_id).values('approval')
        # print(spe)
        spea = spe[0]['approval']
        # print(spea)
        if spea == 1:
            print("logs will be maintained")

        if request.method == 'POST':
            descform = Articles2Form(
                request.POST, instance=get_object_or_404(Articles2, id=event_id))

            # print('descform',descform.is_valid())
            # print('=======')

            if not descform.is_valid():
                return render(request, 'dashboard/edit_event_four.html', {'descform': descform, 'flag': True})
            d1 = (descform.cleaned_data.get('description'))
            # print(d1)
            # d1 = d1[3:]
            # d1 = d1[:-4]
            print(d1)
            if spea == 1:
                log = EventEditLogs(old_data=d, new_data=d1, parameter="description", taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()
            descform.save()
            # h=request.POST.get('b1','')
            # print(h)

            

            return render(request, 'dashboard/edit_event_four.html', {'event_id': event_id, 'descform': descform, 'd': d1, 'bank_regex1': bank_regex1, 'bank_regex2': bank_regex2, 'event_name':event_name})

        # @author Shubham
        # d = d.replace('\n','<br/>')
        # d = '/p>'
        # d = d.replace("\n","")
        # d = d.replace(" ", "")
        # d = '&nbsp;ashdkahkdhkasd</p> kashdjahdj'
        # ends here ~ @author Shubham
        return render(request, 'dashboard/edit_event_four.html', {'event_id': event_id, 'descform': descform, 'd': d, 'bank_regex1': bank_regex1, 'bank_regex2': bank_regex2, 'event_name':event_name})
    except Exception as e:
        print('error in step 4 >>',e)
        return render(request, 'dashboard/edit_event_four.html', {'event_id': event_id, 'descform': descform, 'd': d, 'bank_regex1': bank_regex1, 'bank_regex2': bank_regex2, 'event_name':event_name})

def edit_event_five(request, event_id, ticket_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    now = datetime.now()
    inst = get_object_or_404(Articles2, id=event_id)
    # date11 = inst.sdate.strftime('%m/%d/%Y')
    # sdate11 = inst.sdate.strftime('%d/%m/%Y')

    date = inst.sdate.strftime('%m/%d/%Y')
    sdate = inst.sdate.strftime('%d/%m/%Y')
    edate = inst.edate.strftime('%d/%m/%Y')
    eventStartTime = inst.start_time.strftime('%H:%M')
    eventEndTime = inst.end_time.strftime('%H:%M')
    eventName = inst.event_name

    spe = StatusPromotionTicketing.objects.all().filter(
        event_id=event_id).values('approval')
    spea = spe[0]['approval']
    print(spea)
    if spea == 1:
        print("logs will be maintained")

    print(event_id)
    print(ticket_id)

    allTicketsDetailFilter = Tickets.objects.all().filter(event_id=event_id)
    names = []
    for i in range(0,len(allTicketsDetailFilter)):
        names.append(allTicketsDetailFilter.values('ticket_name')[i]['ticket_name'])
    ticketnames = json.dumps(names)

    d = Tickets.objects.all().filter(tickets_id=ticket_id)
    print(d)
    s = []
    s.append(d.values('ticket_name')[0]['ticket_name'])

    s.append(d.values('ticket_price')[0]['ticket_price'])
    s.append(d.values('other_charges')[0]['other_charges'])
    s.append(d.values('other_charges_type')[0]['other_charges_type'])
    s.append(d.values('ticket_qty')[0]['ticket_qty'])
    s.append(d.values('min_qty')[0]['min_qty'])
    s.append(d.values('max_qty')[0]['max_qty'])
    k = d.values('ticket_start_date')[0]['ticket_start_date']
    sl = now.replace(hour=k.hour, minute=k.minute, second=k.second,
                     microsecond=k.microsecond, year=k.year, month=k.month, day=k.day)
    # sd=datetime.date(k)
    print(sl)
    if k.month < 10:
        if k.day < 10:
            sda = '0' + str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
        else:
            sda = str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
    else:
        if k.day < 10:
            sda = '0' + str(k.day) + '/' + str(k.month) + '/' + str(k.year)
        else:
            sda = str(k.day) + '/' + str(k.month) + '/' + str(k.year)
    s.append(sda)
    print(sda)
    q = datetime.time(k)
    s.append(q)
    # s.append(d.values('start_time')[0]['start_time'])
    k1 = d.values('expiry_date')[0]['expiry_date']
    el = now.replace(hour=k1.hour, minute=k1.minute, second=k1.second,
                     microsecond=k1.microsecond, year=k1.year, month=k1.month, day=k1.day)

    # ed=datetime.date(k1)
    # print(ed)
    if k1.month < 10:
        if k1.day < 10:
            eda = '0' + str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
        else:
            eda = str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
    else:
        if k1.day < 10:
            eda = '0' + str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
        else:
            eda = str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
    s.append(eda)
    print(eda)
    r = datetime.time(k1)
    s.append(r)
    print(r)
    msg = d.values('ticket_msg')[0]['ticket_msg']
    if msg == "None" or msg == "NULL" or msg == "" or msg == None:
        msg = "1"
    s.append(msg)
    s.append(d.values('ticket_label')[0]['ticket_label'])

    print(s)

    if request.method == 'POST':
        print(event_id)
        now = datetime.now()
        # a=Tickets.objects.all().filter(event_id=event_id).values('tickets_id')
        # t_id=a[0]['tickets_id']
        # print(t_id)
        l = []
        t = Tickets.objects.get(tickets_id=ticket_id)
        ticket_name = request.POST.get('ticket_name', '')
        l.append(ticket_name)
        ticket_price = request.POST.get('ticket_price', '')
        l.append(ticket_price)
        other_charges = request.POST.get('other_charges', '')
        l.append(other_charges)
        other_charges_type = request.POST.get('other_charges_type', '')
        l.append(int(other_charges_type))
        ticket_qty = request.POST.get('ticket_qty', '')
        l.append(int(ticket_qty))
        min_qty = request.POST.get('min_qty', '')
        l.append(int(min_qty))
        max_qty = request.POST.get('max_qty', '')
        l.append(int(max_qty))

        tsd = request.POST.get('start_date')
        start_t = request.POST.get('start_time_step5')

        if start_t[0] == '1' and start_t[1] != ':':
            if start_t[6:] == 'AM' and start_t[:2] != '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'AM' and start_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                start_time = now.time().replace(hour=0, minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'PM' and start_t[:2] == '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[:2]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
        else:
            if start_t[5:] == 'AM':
                start_time = now.time().replace(hour=int(start_t[0]), minute=int(
                    start_t[2:4]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[0]) + 12), minute=int(start_t[2:4]), second=0, microsecond=0)

        st = str(start_time)
        sd = request.POST.get('end_date')
        end_t = request.POST.get('end_time_step5')

        if end_t[0] == '1' and end_t[1] != ':':
            if end_t[6:] == 'AM' and end_t[:2] != '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'AM' and end_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                end_time = now.time().replace(hour=0, minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'PM' and end_t[:2] == '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[:2]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
        else:
            if end_t[5:] == 'AM':
                end_time = now.time().replace(hour=int(end_t[0]), minute=int(
                    end_t[2:4]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[0]) + 12), minute=int(end_t[2:4]), second=0, microsecond=0)

        o = str(end_time)
        print(tsd + st)
        print(type(l), st)
        ticket_start_date = tsd + " " + st
        ticket_start_date = datetime.strptime(
            ticket_start_date, '%d/%m/%Y %H:%M:%S')
        l.append(ticket_start_date)
        expiry_date = sd + " " + o
        expiry_date = datetime.strptime(expiry_date, '%d/%m/%Y %H:%M:%S')
        l.append(expiry_date)
        print(ticket_start_date, expiry_date)

        ticket_msg = request.POST.get('ticket_msg', '')
        l.append(ticket_msg)
        ticket_label = request.POST.get('ticket_label', '')
        l.append(ticket_label)
        print(l)
        par = ['ticket_name', 'ticket_price', 'other_charges', 'other_charges_type', 'ticket_qty',
               'min_qty', 'max_qty', 'ticket_start_date', 'expiry_date', 'ticket_msg', 'ticket_label']

        for i in range(0, len(l) - 4):
            print(l[i], s[i])

        if l[0] != s[0]:
            print("0")
            t.ticket_name = ticket_name
            print(par[0], l[0], s[0])
            if spea == 1:
                log = EventEditLogs(old_data=s[0], new_data=l[0], parameter=par[0], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[1] != s[1]:
            print("1")
            t.ticket_price = ticket_price
            print(par[1], l[1], s[1])
            if spea == 1:
                log = EventEditLogs(old_data=s[1], new_data=l[1], parameter=par[1], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[2] != s[2]:
            print("2")
            t.other_charges = other_charges
            print(par[2], l[2], s[2])
            if spea == 1:
                log = EventEditLogs(old_data=s[2], new_data=l[2], parameter=par[2], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[3] != s[3]:
            print("3")
            t.other_charges_type = other_charges_type
            print(par[3], l[3], s[3])
            if spea == 1:
                log = EventEditLogs(old_data=s[3], new_data=l[3], parameter=par[3], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[4] != s[4]:
            print("4")
            t.ticket_qty = ticket_qty
            print(par[4], l[4], s[4])
            if spea == 1:
                log = EventEditLogs(old_data=s[4], new_data=l[4], parameter=par[4], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[5] != s[5]:
            print("5")
            t.min_qty = min_qty
            print(par[5], l[5], s[5])
            if spea == 1:
                log = EventEditLogs(old_data=s[5], new_data=l[5], parameter=par[5], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[6] != s[6]:
            print("6")
            t.max_qty = max_qty
            print(par[6], l[6], s[6])
            if spea == 1:
                log = EventEditLogs(old_data=s[6], new_data=l[6], parameter=par[6], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[7] != sl:
            print("7")
            t.ticket_start_date = ticket_start_date
            print(par[7], l[7], sl)
            if spea == 1:
                log = EventEditLogs(old_data=sl, new_data=l[7], parameter=par[7], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[8] != el:
            print("8")
            t.expiry_date = expiry_date
            print(par[8], l[8], el)
            if spea == 1:
                log = EventEditLogs(old_data=el, new_data=l[8], parameter=par[8], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[9] != s[11]:
            print("9")
            t.ticket_msg = ticket_msg
            print(par[9], l[9], s[11])
            if spea == 1:
                log = EventEditLogs(old_data=s[11], new_data=l[9], parameter=par[9], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        if l[10] != s[12]:
            print("10")
            t.ticket_label = ticket_label
            print(par[10], l[10], s[12])
            if spea == 1:
                log = EventEditLogs(old_data=s[12], new_data=l[10], parameter=par[10], taken_action='update',
                                    event_id=event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

        print(l, s)

        t.save()

        return HttpResponseRedirect(reverse('dashboard:edit-event-ticket', args=(event_id,)))
    return render(request, 'dashboard/edit_event_five.html', {'event_id': event_id, 'ticket_id': ticket_id, 'event_start_date':date, 'sdate':sdate, 'edate':edate,'event_start_time':eventStartTime,'event_end_time':eventEndTime, 's': s, 'ticketnames':ticketnames, 'event_name':eventName})


def edit_action_three(request, event_id):

    print(event_id)

    return HttpResponseRedirect(reverse('dashboard:edit-event-four', args=(event_id,)))


def delete_ticket(request, md5, event_id, ticket_id, return_page):

    t = Tickets.objects.get(tickets_id=ticket_id)
    t.delete()
    # delele coupon code on delete of tickets
    try:
        TicketDiscounts.objects.get(ticket_id=ticket_id).delete()
    except:
        print('discount was not available with recently deleted ticket')
    # ends here ~ delele coupon code on delete of tickets
    if return_page == 0:
        # return HttpResponseRedirect(reverse('dashboard:step_five', args=(md5,event_id)))
        return redirect(request.META['HTTP_REFERER'])
    elif return_page == 1:
        return HttpResponseRedirect(reverse('dashboard:edit-event-ticket', args=(event_id,)))


def edit_event_ticket(request, event_id):

    print(event_id)
    id = []
    name = []
    price = []
    currency = []
    eventStartDate = []
    eventStart_date = ''

    country = Articles2.objects.all().filter(id=event_id).values('country')
    country = country[0]['country']

    # get event name from articles 2 table
    articles2Filter = Articles2.objects.get(id=event_id)
    event_name = articles2Filter.event_name
    # ends here ~ get event name from articles 2 table

    print(country)
    currency = AboutCountries.objects.all().filter(
        country=country).values('currency')
    print(currency)
    if len(currency) != 0:
        currency = currency[0]['currency']
    print(currency)
    tick = Tickets.objects.all().filter(event_id=event_id)
    print('tick')
    print(list(tick))

    # tkts = Tickets.objects.all().filter(event_id = event_id)
    # print(tkts)
    # tkt_name = []
    # tkt_price = []
    # oth_chrgs = []
    # oth_chrgs_type =[]
    # tkt_qty = []
    # min_qty = []
    # max_qty = []
    # tkt_left = []
    # tkt_msg = []
    # s_date = []
    # e_date = []
    # e_fee = []
    # trans_fee = []
    # tkt_lbl = []
    # activ = []

    # for i in tkts:
    #     tkt_name.append(i.ticket_name)
    #     tkt_price.append(i.ticket_price)
    #     oth_chrgs.append(i.other_charges)
    #     oth_chrgs_type.append(i.other_charges_type)
    #     tkt_qty.append(i.ticket_qty)
    #     min_qty.append(i.min_qty)
    #     max_qty.append(i.max_qty)
    #     tkt_left.append(i.qty_left)
    #     tkt_msg.append(i.ticket_msg)
    #     s_date.append(i.ticket_start_date)
    #     e_date.append(i.expiry_date)
    #     e_fee.append(i.ercess_fee)
    #     trans_fee.append(i.transaction_fee)
    #     tkt_lbl.append(i.ticket_label)
    #     activ.append(i.active)
    # print("message-------------")
    # print(len(tkt_name), len(tkt_price), len(oth_chrgs),
    #                 len(oth_chrgs_type), len(tkt_qty), len(min_qty),
    #                 len(max_qty), len(tkt_left),len(tkt_msg), len(s_date), len(e_date),
    #                 len(e_fee), len(trans_fee), len(tkt_lbl), len(activ))
    # print(oth_chrgs)
    # print("message-------------")
    tktStartDate = []
    tktEndDate = []
    for i in range(0, len(tick)):
        print(i)
        id.append(tick.values('tickets_id')[i]['tickets_id'])
        name.append(tick.values('ticket_name')[i]['ticket_name'])
        price.append(tick.values('ticket_price')[i]['ticket_price'])
        tktStartDate.append(tick.values('ticket_start_date')[i]['ticket_start_date'])
        tktEndDate.append(tick.values('expiry_date')[i]['expiry_date'])

    eventStart_date = Articles2.objects.all().filter(id=event_id).values('sdate')
    eventStart_date = eventStart_date[0]['sdate']
    ticks = zip(id, name, price, tktStartDate, tktEndDate)

    # new code ~ nov 30 ~ author shubham
    statusPromoFilter = StatusPromotionTicketing.objects.get(event_id=event_id)
    ticketStatus = statusPromoFilter.ticketing
    # ends here ~ nov 30 ~ author shubham

    return render(request, 'dashboard/edit_event_ticket.html', {'event_id': event_id, 'currency': currency, 'ticks': ticks, 'eventStart_date':eventStart_date ,'ticketStatus':ticketStatus, 'event_name':event_name})


def new_ticket(request, event_id):
    print('---------------------------------------','userid' not in request.session.keys(),request.session)
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    event_id = event_id
    print("len(tick)")
    inst = get_object_or_404(Articles2, id=event_id)
    # date11 = inst.sdate.strftime('%m/%d/%Y')
    # sdate11 = inst.sdate.strftime('%d/%m/%Y')

    date = inst.sdate.strftime('%m/%d/%Y')
    sdate = inst.sdate.strftime('%d/%m/%Y')
    edate = inst.edate.strftime('%d/%m/%Y')
    eventStartTime = inst.start_time.strftime('%H:%M')
    eventEndTime = inst.end_time.strftime('%H:%M')
    eventName = inst.event_name

    aboutcountries = AboutCountries.objects.all()
    now = datetime.now()

    if request.method == 'POST':
        print(event_id)
        now = datetime.now()
        # a=Tickets.objects.all().filter(event_id=event_id).values('tickets_id')
        # t_id=a[0]['tickets_id']
        # print(t_id)
        l = []
        # t= Tickets.objects.get(tickets_id = ticket_id)
        ticket_name = request.POST.get('ticket_name', '')
        l.append(ticket_name)
        ticket_price = request.POST.get('ticket_price', '')
        l.append(ticket_price)
        other_charges = request.POST.get('other_charges', '')
        l.append(other_charges)
        other_charges_type = request.POST.get('other_charges_type', '')
        l.append(int(other_charges_type))
        ticket_qty = request.POST.get('ticket_qty', '')
        l.append(int(ticket_qty))
        min_qty = request.POST.get('min_qty', '')
        l.append(int(min_qty))
        max_qty = request.POST.get('max_qty', '')
        l.append(int(max_qty))

        tsd = request.POST.get('start_date')
        start_t = request.POST.get('start_time_step5')


        if start_t[0] == '1' and start_t[1] != ':':
            if start_t[6:] == 'AM' and start_t[:2] != '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'AM' and start_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                start_time = now.time().replace(hour=0, minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'PM' and start_t[:2] == '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[:2]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
        else:
            if start_t[5:] == 'AM':
                start_time = now.time().replace(hour=int(start_t[0]), minute=int(
                    start_t[2:4]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[0]) + 12), minute=int(start_t[2:4]), second=0, microsecond=0)

        st = str(start_time)
        sd = request.POST.get('end_date')
        end_t = request.POST.get('end_time_step5')


        if end_t[0] == '1' and end_t[1] != ':':
            if end_t[6:] == 'AM' and end_t[:2] != '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'AM' and end_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                end_time = now.time().replace(hour=0, minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'PM' and end_t[:2] == '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[:2]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
        else:
            if end_t[5:] == 'AM':
                end_time = now.time().replace(hour=int(end_t[0]), minute=int(
                    end_t[2:4]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[0]) + 12), minute=int(end_t[2:4]), second=0, microsecond=0)

        o = str(end_time)
        print(o)
        print(tsd + st)
        print (end_t)

        print(type(l), st)
        ticket_start_date = tsd + " " + st
        ticket_start_date = datetime.strptime(
            ticket_start_date, '%d/%m/%Y %H:%M:%S')
        l.append(ticket_start_date)
        expiry_date = sd + " " + o
        expiry_date = datetime.strptime(expiry_date, '%d/%m/%Y %H:%M:%S')
        l.append(expiry_date)
        print(ticket_start_date, expiry_date)
        print(' l >> ',l)

        ticket_msg = request.POST.get('ticket_msg', '')
        l.append(ticket_msg)
        ticket_label = request.POST.get('ticket_label', '')
        l.append(ticket_label)
        print(l)
        tk = Tickets(event_id=event_id, ticket_name=l[0], ticket_price=l[1], other_charges=l[2], other_charges_type=l[3], ticket_qty=l[4], min_qty=l[5],
                     max_qty=l[6], qty_left=l[4], ticket_msg=l[9], ticket_start_date=l[7], expiry_date=l[8], ercess_fee=1, transaction_fee=1, ticket_label=l[10], active=1)
        tk.save()

        return HttpResponseRedirect(reverse('dashboard:edit-event-ticket', args=(event_id,)))

    return render(request, 'dashboard/new_ticket.html', {'event_id': event_id, 'a': aboutcountries,'event_start_date':date, 'sdate':sdate, 'edate':edate,'event_start_time':eventStartTime,'event_end_time':eventEndTime, 'event_name':eventName})


def edit_action_five(request, event_id, ticket_id):

    # print(event_id)
    # now = datetime.now()
    # # a=Tickets.objects.all().filter(event_id=event_id).values('tickets_id')
    # # t_id=a[0]['tickets_id']
    # # print(t_id)
    # t= Tickets.objects.get(tickets_id = ticket_id)
    # ticket_name=request.POST.get('ticket_name','')

    # tsd = request.POST.get('start_date')
    # start_t = request.POST.get('start_time_step5')

    # if start_t[0] == '1' and start_t[1] != ':':
    #     if start_t[6:] == 'AM' and start_t[:2] != '12':
    #         start_time = now.time().replace(hour=int(start_t[:2]), minute=int(start_t[3:5]), second=0, microsecond=0)
    #     elif start_t[6:] == 'AM' and start_t[:2] == '12':
    #         # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
    #         start_time = now.time().replace(hour=0, minute=int(start_t[3:5]), second=0, microsecond=0)
    #     elif start_t[6:] == 'PM' and start_t[:2] == '12':
    #         start_time = now.time().replace(hour=int(start_t[:2]), minute=int(start_t[3:5]), second=0, microsecond=0)
    #     else:
    #         start_time = now.time().replace(hour=(int(start_t[:2]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
    # else:
    #     if start_t[5:] == 'AM':
    #         start_time = now.time().replace(hour=int(start_t[0]), minute=int(start_t[2:4]), second=0, microsecond=0)
    #     else:
    #         start_time = now.time().replace(hour=(int(start_t[0]) + 12), minute=int(start_t[2:4]), second=0, microsecond=0)

    # l=str(start_time)
    # sd = request.POST.get('end_date')
    # end_t = request.POST.get('end_time_step5')

    # if end_t[0] == '1' and end_t[1] != ':':
    #     if end_t[6:] == 'AM' and end_t[:2] != '12':
    #         end_time = now.time().replace(hour=int(end_t[:2]), minute=int(end_t[3:5]), second=0, microsecond=0)
    #     elif end_t[6:] == 'AM' and end_t[:2] == '12':
    #         # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
    #         end_time = now.time().replace(hour=0, minute=int(end_t[3:5]), second=0, microsecond=0)
    #     elif end_t[6:] == 'PM' and end_t[:2] == '12':
    #         end_time = now.time().replace(hour=int(end_t[:2]), minute=int(end_t[3:5]), second=0, microsecond=0)
    #     else:
    #         end_time = now.time().replace(hour=(int(end_t[:2]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
    # else:
    #     if end_t[5:] == 'AM':
    #         end_time = now.time().replace(hour=int(end_t[0]), minute=int(end_t[2:4]), second=0, microsecond=0)
    #     else:
    #         end_time = now.time().replace(hour=(int(end_t[0]) + 12), minute=int(end_t[2:4]), second=0, microsecond=0)

    # o=str(end_time)
    # print(tsd + l )
    # print(type(l),l)
    # ticket_start_date = tsd +" "+ l
    # ticket_start_date = datetime.strptime(ticket_start_date, '%d/%m/%Y %H:%M:%S')
    # expiry_date= sd +" "+ o
    # expiry_date= datetime.strptime(expiry_date, '%d/%m/%Y %H:%M:%S')
    # print(ticket_start_date,expiry_date)

    # ticket_price=request.POST.get('ticket_price','')
    # other_charges=request.POST.get('other_charges','')
    # other_charges_type=request.POST.get('other_charges_type','')
    # ticket_qty=request.POST.get('ticket_qty','')
    # min_qty=request.POST.get('min_qty','')
    # max_qty=request.POST.get('max_qty','')
    # ticket_msg=request.POST.get('ticket_msg','')
    # ticket_label=request.POST.get('ticket_label','')
    # print(ticket_label)

    # t.ticket_name = ticket_name
    # t.ticket_start_date = ticket_start_date
    # t.expiry_date = expiry_date
    # t.ticket_price = ticket_price
    # t.other_charges = other_charges
    # t.other_charges_type = other_charges_type
    # t.ticket_qty = ticket_qty
    # t.min_qty = min_qty
    # t.max_qty = max_qty
    # t.ticket_msg = ticket_msg
    # t.ticket_label = ticket_label
    # t.save()

    return HttpResponseRedirect(reverse('dashboard:edit-event-five', args=(event_id, ticket_id)))


def edit_action_four(request, event_id):

    print(event_id)

    return HttpResponseRedirect(reverse('dashboard:edit-event-four', args=(event_id,)))


def step_three(request, md5, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    # get event name from articles 2 table
    articles2Filter = Articles2.objects.get(id=event_id)
    event_name = articles2Filter.event_name
    # ends here ~ get event name from articles 2 table

    logging.debug('Just above Post method code')

    if request.method == 'POST':
        logging.debug('Post method is working')
        logging.debug('{} {}'.format(event_id, md5))

        articles2 = Articles2.objects.get(id=event_id)
        logging.debug('getting access to db')
        event_name = re.sub('[^A-Za-z0-9 ]+', '', articles2.event_name)
        event_name = event_name.replace(' ', '-')
        image_name = event_name + '-' + str(event_id)
        print(image_name)
        uploadedfileurl = ''

        if request.method == 'POST' and request.FILES.get('myfile', None):
            logging.debug('Inside banner image code')
            myfile = request.FILES['myfile']
            logging.debug('{}'.format(myfile))
            logging.debug(myfile.name.split('.'))
            image_name_banner = image_name + '-' + \
                'banner' + '.' + myfile.name.split('.')[-1]
            logging.debug(
                'banner image name will be saved as: {}'.format(image_name_banner))
            # logging.debug(image_name_banner)
            myfile.name = image_name_banner
            x_s = request.POST.get('x', '')
            y_s = request.POST.get('y', '')
            w_s = request.POST.get('width', '')
            h_s = request.POST.get('height', '')

            print('x_s > ',x_s)
            print('y_s > ',y_s)
            print('w_s > ',w_s)
            print('h_s > ',h_s)

            # return False

            if(x_s == None or x_s == ''):
                x = 0
                y = 0
            else:
                x = float(x_s)
                y = float(y_s)
            w = float(w_s)
            h = float(h_s)
            print(myfile.name)
            image = Image.open(myfile)
            cropped_image = image.crop((x, y, w + x, h + y))
            resized_image = cropped_image.resize((1600, 900), Image.ANTIALIAS)

            fs = FileSystemStorage(location='media')
            # logging.debug('File system storage data: {}'.format(fs))
            # # logging.debug(fs)
            # fs.save(myfile.name,resized_image)
            resized_image.name = myfile.name
            BASE_DIR = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            MEDIA_DIR = os.path.join(BASE_DIR, 'media')
            print(MEDIA_DIR)
            resized_image.convert('RGB').save(MEDIA_DIR + "/" + resized_image.name, format='PNG')
            filename = resized_image.name
            logging.debug('final name: {}'.format(filename))
            # logging.debug(filename)
            uploadedfileurl = fs.url(filename)
            u_banner = uploadedfileurl
        # logging.debug(u_banner)
        logging.debug('Saved url in db: {}'.format(u_banner))

        myfile1 = request.POST.get('myfile1', None)

        print(myfile1)
        uploadedfileurl_1 = ''
        u_p = ''
        if request.method == 'POST' and request.FILES.get('myfile1', None):
            myfile1 = request.FILES['myfile1']
            image_name_thumb = image_name + '-' + \
                'thumbnail' + '.' + myfile1.name.split('.')[-1]
            print(image_name_thumb)
            myfile1.name = image_name_thumb

            # new code
            x_s_thumb = request.POST.get('x_p', '')
            y_s_thumb = request.POST.get('y_p', '')
            w_s_thumb = request.POST.get('width_p', '')
            h_s_thumb = request.POST.get('height_p', '')

            if(x_s_thumb == None or x_s_thumb == ''):
                x_s = 0
                y_s = 0
            else:
                x_s = float(x_s_thumb)
                y_s = float(y_s_thumb)
            w_s = float(w_s_thumb)
            h_s = float(h_s_thumb)

            image = Image.open(myfile1)
            cropped_image = image.crop((x_s, y_s, w_s + x_s, h_s + y_s))
            resized_image_thumb = cropped_image.resize((1600, 900), Image.ANTIALIAS)

            # ends here ~ new code

            fs_1 = FileSystemStorage(location='media')

            # new code
            resized_image_thumb.name = myfile1.name
            BASE_DIR = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            MEDIA_DIR = os.path.join(BASE_DIR, 'media')
            resized_image_thumb.save(MEDIA_DIR + "/" + resized_image_thumb.name, format='PNG')
            filename_1 = resized_image_thumb.name
            # logging.debug(filename)
            uploadedfileurl_1 = fs_1.url(filename_1)
            u_p = uploadedfileurl_1
            # ends here ~ new code

            # filename_1 = fs_1.save(myfile1.name, myfile1)
            # uploadedfileurl_1 = fs_1.url(filename_1)
            # u_p = uploadedfileurl_1

        myfile2 = request.POST.get('myfile2', None)

        print(myfile2)
        uploadedfileurl_2 = ''
        u_editables = ''
        if request.method == 'POST' and request.FILES.get('myfile2', None):
            myfile2 = request.FILES['myfile2']
            editable_name = image_name + '-' + 'editable' + \
                '.' + myfile2.name.split('.')[-1]
            print(editable_name)
            myfile2.name = editable_name
            fs_2 = FileSystemStorage(location='media/editables')
            filename2 = fs_2.save(myfile2.name, myfile2)
            uploadedfileurl_2 = fs_2.url(filename2)
            u_editables = uploadedfileurl_2

        u_editables = uploadedfileurl_2.replace("/media/", "/media/editables/")
        articles2.banner = u_banner
        articles2.profile_image = u_p
        articles2.editable_image = u_editables
        # s=Articles2(id=event_id,banner=u_banner,profile_image=u_p,editable_image=u_editables)

        # print(s)
        articles2.save()

        # return render(request, 'dashboard/create-event/step_3/step_three_temp.html',{'event_id':event_id, 'md5':md5,})
        # return redirect('/live/dashboard/add-event-description/67a6687ee9ff3f3d54eb361752c9fcd1/36679')
        #base_url = reverse('dashboard:step_four', kwargs={'md5':md5, 'event_id':event_id})
        # print(base_url)

        # return redirect(base_url)
        StatusPromotionTicketing.objects.filter(event_id=event_id).update(step1_complete = 1, step2_complete = 1, step3_complete = 1)

        return redirect(reverse('dashboard:step_four', kwargs={'md5': md5, 'event_id': event_id}))

    return render(request, 'dashboard/create-event/step_3/step_three_temp.html', {'event_id': event_id, 'md5': md5, 'event_name':event_name})


def step_three_action(request, md5, event_id):

    print(event_id, md5)
    # myfile=request.POST.get('myfile', None)
    # articles2 = Articles2.objects.get(id = event_id)
    # event_name = re.sub('[^A-Za-z0-9 ]+', '',articles2.event_name)
    # event_name = event_name.replace(' ','-')
    # image_name = event_name +'-'+str(event_id)
    # uploadedfileurl=''

    # if request.method=='POST' and request.FILES.get('myfile', None):
    #     myfile=request.FILES['myfile']
    #     print(myfile.name.split('.'))
    #     image_name_banner = image_name +'-' + 'banner' + '.' + myfile.name.split('.')[-1]
    #     print(image_name_banner)
    #     myfile.name = image_name_banner
    #     fs=FileSystemStorage(location='media/events/images')
    #     print(fs)
    #     filename=fs.save(myfile.name,myfile)
    #     print(filename)
    #     uploadedfileurl=fs.url(filename)
    #     u_banner=uploadedfileurl
    # print(u_banner)

    # myfile1=request.POST.get('myfile1', None)

    # print(myfile1)
    # uploadedfileurl_1=''
    # u_p=''
    # if request.method=='POST' and request.FILES.get('myfile1', None):
    #     myfile1=request.FILES['myfile1']
    #     image_name_thumb = image_name +'-' + 'thumbnail' + '.' + myfile1.name.split('.')[-1]
    #     print(image_name_thumb)
    #     myfile1.name = image_name_thumb
    #     fs_1=FileSystemStorage(location='media/events/images')
    #     filename_1=fs_1.save(myfile1.name,myfile1)
    #     uploadedfileurl_1=fs_1.url(filename_1)
    #     u_p =uploadedfileurl_1

    # myfile2=request.POST.get('myfile2', None)

    # print(myfile2)
    # uploadedfileurl_2=''
    # u_editables=''
    # if request.method=='POST' and request.FILES.get('myfile2', None):
    #     myfile2=request.FILES['myfile2']
    #     editable_name = image_name +'-' + 'editable' + '.' + myfile2.name.split('.')[-1]
    #     print(editable_name)
    #     myfile2.name = editable_name
    #     fs_2=FileSystemStorage(location='media/events/editables')
    #     filename2=fs_2.save(myfile2.name,myfile2)
    #     uploadedfileurl_2=fs_2.url(filename2)
    #     u_editables=uploadedfileurl_2

    # articles2.banner = u_banner
    # articles2.profile_image = u_p
    # articles2.editable_image = u_editables
    # #s=Articles2(id=event_id,banner=u_banner,profile_image=u_p,editable_image=u_editables)

    # #print(s)
    # articles2.save()

    # #return render(request, 'dashboard/create-event/step_3/step_three_temp.html',{'event_id':event_id, 'md5':md5,})
    # #return redirect('/live/dashboard/add-event-description/67a6687ee9ff3f3d54eb361752c9fcd1/36679')
    # #base_url = reverse('dashboard:step_four', kwargs={'md5':md5, 'event_id':event_id})
    # #print(base_url)

    # #return redirect(base_url)
    return redirect(reverse('dashboard:step_four', kwargs={'md5': md5, 'event_id': event_id}))

###################################################################################


def create_stall(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    return render(request, 'dashboard/create-stalls.html')

####################################################################################


def organizer_agreement(request):

    return render(request, 'dashboard/organizer-agreement.html')


#######################################################################################

def getSalesDetails(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    event = Articles2.objects.all().filter(id=event_id).first()
    print(event)
    eve_name = event.event_name
    print(eve_name)
    # @author Shubham
    sales = TicketsSale.objects.all().filter(event_id=event_id)
    # sales = Tickets_Sale.objects.all().filter(event_id=event_id)
    # ends here ~ @author Shubham
    print(sales)
    t_count = len(sales)
    print(t_count)

    tkt_type = []
    tkt_qty = []
    tkt_amt = []
    tkt_p_date = []
    tkt_s_site = []
    tkt_atendee = []
    tkt_contact = []
    tkt_email = []
    tkt_book_id = []

    if t_count != 0:
        for i in sales:
            print(i)
            tkt_book_id.append(i.booking_id)
            tkt_type.append(i.ticket_type)
            tkt_amt.append(i.ampunt_paid)
            tkt_qty.append(i.qty)
            tkt_p_date.append(i.purchase_date)
            tkt_s_site.append(i.seller_site)
            tkt_atendee.append(i.attendee_name)
            tkt_contact.append(i.attendee_contact)
            tkt_email.append(i.attendee_email)

    details = zip(tkt_type, tkt_book_id, tkt_amt, tkt_qty,
                  tkt_p_date, tkt_s_site, tkt_atendee, tkt_contact, tkt_email)
    return render(request, 'sale_detail.html', {'details': details, 'count': t_count, 'eve_name': eve_name})


########################################### boost event button ########################################

def boost(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    c = Articles2.objects.all().filter(id=event_id).values('city')
    ac = BoostEvent.objects.all().filter(event_id=event_id)
    print(len(ac))
    if len(ac) == 4:
        # print('\n\n\n','vinayak','\n\n\n\n')
        #  WARNING:  message for user
        messages.warning(request, "can't add more citys")
    else:
        if request.method == "POST":
            form = BoostEventForm(request.POST)
            if form.is_valid():
                ei = form.save(commit=False)
                ei.event_id = event_id
                # print('\n\n\n',form,'\n\n\n\n')
                ei.save()
                #####can't redirect because we need to pass values ##############
                c = Articles2.objects.all().filter(id=event_id).values('city')
                ac = BoostEvent.objects.all().filter(event_id=event_id)
                form = BoostEventForm()
                return render(request, 'dashboard/boost_event.html', {'event_id': event_id, 's': c, 'ac': ac, 'form': form})
    form = BoostEventForm()

    return render(request, 'dashboard/boost_event.html', {'event_id': event_id, 's': c, 'ac': ac, 'form': form})



###########################update contact##############################
def updateMobileNo(request):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    if request.method == "POST":
        form = UpdateContact(request.POST)
        if form.is_valid():
            #######################contact#########################
            user = Users.objects.get(pk=request.session['userid'])
            user.mobile = request.POST['mobile']
            print('\n\n\n\n\n\n\n',user.mobile,'/t vinayak')
            user.save()
            #######################################################

            # @author Shubham ~ send email on updating mobile number ~ october 12 2019
            subject = 'Your contact number is linked with Ercess Live account successfully'
            email_from = conf_settings.EMAIL_HOST_USER
            recipient_list = [user.user]

            html_message = render_to_string('static/common/contactnumber_added_temp.html')

            msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
            msg.content_subtype = "html"
            msg.send(fail_silently=False)
            # ends here ~ @author Shubham ~ send email on updating mobile number ~ october 12 2019

            return HttpResponseRedirect(reverse('dashboard:step_one'))
        else:
            return render(request,'dashboard/updateContact.html',{'form':form})

    else:
        form =  UpdateContact()
        return render(request,'dashboard/updateContact.html',{'form':form})


########################################################################

def update_event_tickets(request, md5, event_id, ticket_id):
    if request.method == 'POST':
        print(event_id)
        now = datetime.now()
        # a=Tickets.objects.all().filter(event_id=event_id).values('tickets_id')
        # t_id=a[0]['tickets_id']
        # print(t_id)
        l = []
        t = Tickets.objects.get(tickets_id=ticket_id)
        ticket_name = request.POST.get('ticket_name', '')
        l.append(ticket_name)
        ticket_price = request.POST.get('ticket_price', '')
        l.append(ticket_price)
        other_charges = request.POST.get('other_charges', '')
        l.append(other_charges)
        other_charges_type = request.POST.get('other_charges_type', '')
        l.append(int(other_charges_type))
        ticket_qty = request.POST.get('ticket_qty', '')
        l.append(int(ticket_qty))
        min_qty = request.POST.get('min_qty', '')
        l.append(int(min_qty))
        max_qty = request.POST.get('max_qty', '')
        l.append(int(max_qty))

        tsd = request.POST.get('start_date')
        start_t = request.POST.get('start_time_step5')

        if start_t[0] == '1' and start_t[1] != ':':
            if start_t[6:] == 'AM' and start_t[:2] != '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'AM' and start_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                start_time = now.time().replace(hour=0, minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'PM' and start_t[:2] == '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                    start_t[3:5]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(
                    hour=(int(start_t[:2]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
        else:
            if start_t[5:] == 'AM':
                start_time = now.time().replace(hour=int(start_t[0]), minute=int(
                    start_t[2:4]), second=0, microsecond=0)
            else:
                print(start_t,' <<<<<<<<< 111111111111111111111111111111111 >>>>>>>> ',start_t[2:4])
                start_time = now.time().replace(
                    hour=(int(start_t[0]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
                    # hour=(int(start_t[0]) + 12), minute=int(start_t[2:4]), second=0, microsecond=0)

        st = str(start_time)
        sd = request.POST.get('end_date')
        end_t = request.POST.get('end_time_step5')

        if end_t[0] == '1' and end_t[1] != ':':
            if end_t[6:] == 'AM' and end_t[:2] != '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'AM' and end_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                end_time = now.time().replace(hour=0, minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'PM' and end_t[:2] == '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                    end_t[3:5]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[:2]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
        else:
            if end_t[5:] == 'AM':
                end_time = now.time().replace(hour=int(end_t[0]), minute=int(
                    end_t[2:4]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(
                    hour=(int(end_t[0]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
                    # hour=(int(end_t[0]) + 12), minute=int(end_t[2:4]), second=0, microsecond=0)

        o = str(end_time)
        print(tsd + st)
        print(type(l), st)
        ticket_start_date = tsd + " " + st
        ticket_start_date = datetime.strptime(
            ticket_start_date, '%d/%m/%Y %H:%M:%S')
        l.append(ticket_start_date)
        expiry_date = sd + " " + o
        expiry_date = datetime.strptime(expiry_date, '%d/%m/%Y %H:%M:%S')
        l.append(expiry_date)
        print(ticket_start_date, expiry_date)

        ticket_msg = request.POST.get('ticket_msg', '')
        l.append(ticket_msg)
        ticket_label = request.POST.get('ticket_label', '')
        l.append(ticket_label)
        print(l)
        par = ['ticket_name', 'ticket_price', 'other_charges', 'other_charges_type', 'ticket_qty',
               'min_qty', 'max_qty', 'ticket_start_date', 'expiry_date', 'ticket_msg', 'ticket_label']

        # for i in range(0, len(l) - 4):
        #     print(l[i], s[i])

        t.ticket_name = ticket_name
        t.ticket_price = ticket_price
        t.other_charges = other_charges
        t.other_charges_type = other_charges_type
        t.ticket_qty = ticket_qty
        t.min_qty = min_qty
        t.max_qty = max_qty
        t.ticket_start_date = ticket_start_date
        t.expiry_date = expiry_date
        t.ticket_msg = ticket_msg
        t.ticket_label = ticket_label

        t.save()

        return HttpResponseRedirect(reverse('dashboard:step_five', args=(md5,event_id)))



# code for edit images step 3 on edit event mode
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, 'media')
print('MEDIA_DIR >> ',MEDIA_DIR)
def edit_event_three(request, event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')

    if request.method == 'GET':
        try:
            article = Articles2.objects.get(id=event_id)
            pro_image= article.profile_image
            banner = article.banner
            edit_image = article.editable_image

            # get event name from articles 2 table
            articles2Filter = Articles2.objects.get(id=event_id)
            event_name = articles2Filter.event_name
            # ends here ~ get event name from articles 2 table

            return render(request, 'dashboard/edit_event_three.html', {'pro_image': pro_image, 'banner': banner, 'edit_image':edit_image, 'event_id': event_id, 'event_name':event_name})
            # return render(request, 'dashboard/edit_event_three.html', {'event_id': 'event_id', 'ticket_id': 'ticket_id', 'event_start_date': 'date11', 'sdate': 'sdate11', 's': 's'})
        except:
            return redirect('/live/dashboard/organizer_dashboard')

    if request.method == 'POST':
        articles2 = Articles2.objects.get(id=event_id)
        event_name = re.sub('[^A-Za-z0-9 ]+', '', articles2.event_name)
        event_name = event_name.replace(' ', '-')
        image_name = event_name + '-' + str(event_id)
        print(image_name)
        uploadedfileurl = ''
        u_banner = ''
        if request.method == 'POST' and request.FILES.get('myfile', None):
            myfile = request.FILES['myfile']
            logging.debug('{}'.format(myfile))
            logging.debug(myfile.name.split('.'))
            image_name_banner = image_name + '-' + \
                'banner' + '.' + myfile.name.split('.')[-1]
            logging.debug(
                'banner image name will be saved as: {}'.format(image_name_banner))
            # logging.debug(image_name_banner)
            myfile.name = image_name_banner
            x_s = request.POST.get('x', '')
            y_s = request.POST.get('y', '')
            w_s = request.POST.get('width', '')
            h_s = request.POST.get('height', '')

            if(x_s == None or x_s == ''):
                x = 0
                y = 0
            else:
                x = float(x_s)
                y = float(y_s)
            w = float(w_s)
            h = float(h_s)


            image = Image.open(myfile)
            cropped_image = image.crop((x, y, w + x, h + y))
            # cropped_image = image.crop((x, y, w, h))
            # cropped_image = image.crop((0.0, 100.0, 800.0, 800.0))
            resized_image = cropped_image.resize((1600, 900), Image.ANTIALIAS)

            fs = FileSystemStorage(location='media')
            # logging.debug('File system storage data: {}'.format(fs))
            # # logging.debug(fs)
            # fs.save(myfile.name,resized_image)
            resized_image.name = myfile.name

            # MEDIA_DIR = os.path.join(BASE_DIR, 'media')
            bannerFileFilter = Articles2.objects.filter(id=event_id).values('banner')
            bannerFilterFileName = bannerFileFilter[0]['banner']
            # bannerFilterFileLoc = os.path.join(BASE_DIR, bannerFilterFileName)

            bannerFilterFileLoc = BASE_DIR+bannerFilterFileName
            if (bannerFilterFileLoc != '' and bannerFilterFileLoc != None):
                if os.path.exists(bannerFilterFileLoc):
                    os.remove(bannerFilterFileLoc)

            # if os.path.exists(MEDIA_DIR + "/" + resized_image.name):
            #     os.remove(MEDIA_DIR + "/" + resized_image.name)
            resized_image.convert('RGB').save(MEDIA_DIR + "/" + resized_image.name, format='PNG')
            filename = resized_image.name
            logging.debug('final name: {}'.format(filename))
            # logging.debug(filename)
            uploadedfileurl = fs.url(filename)
            u_banner = uploadedfileurl
            Articles2.objects.filter(id=event_id).update(banner=u_banner)
        # logging.debug(u_banner)
        logging.debug('Saved url in db: {}'.format(u_banner))

        myfile1 = request.POST.get('myfile1', None)

        print(myfile1)
        uploadedfileurl_1 = ''
        u_p = ''
        if request.method == 'POST' and request.FILES.get('myfile1', None):
            ################################################
            ####################OLD CODE####################
            # myfile1 = request.FILES['myfile1']
            # image_name_thumb = image_name + '-' + \
            #     'thumbnail' + '.' + myfile1.name.split('.')[-1]
            # print(image_name_thumb)
            # myfile1.name = image_name_thumb
            # fs_1 = FileSystemStorage(location='media')
            # print(myfile1.name, myfile1)
            # if os.path.exists(MEDIA_DIR + "/" + myfile1.name):
            #     os.remove(MEDIA_DIR + "/" + myfile1.name)
            # filename_1 = fs_1.save(myfile1.name, myfile1)
            # uploadedfileurl_1 = fs_1.url(filename_1)
            # u_p = uploadedfileurl_1
            # Articles2.objects.filter(id=event_id).update(profile_image=u_p)
            ##################ENDS HERE ~ OLD CODE################
            ######################################################

            ######### new code
            myfile1 = request.FILES['myfile1']
            image_name_thumb = image_name + '-' + \
                'thumbnail' + '.' + myfile1.name.split('.')[-1]
            print(image_name_thumb)
            myfile1.name = image_name_thumb

            # new code
            x_s_thumb = request.POST.get('x_p', '')
            y_s_thumb = request.POST.get('y_p', '')
            w_s_thumb = request.POST.get('width_p', '')
            h_s_thumb = request.POST.get('height_p', '')

            if(x_s_thumb == None or x_s_thumb == ''):
                x_thumb = 0
                y_thumb = 0
            else:
                x_thumb = float(x_s_thumb)
                y_thumb = float(y_s_thumb)
            w_thumb = float(w_s_thumb)
            h_thumb = float(h_s_thumb)

            image = Image.open(myfile1)
            cropped_image = image.crop((x_thumb, y_thumb, w_thumb + x_thumb, h_thumb + y_thumb))
            resized_image_thumb = cropped_image.resize((1600, 900), Image.ANTIALIAS)

            # ends here ~ new code

            fs_1 = FileSystemStorage(location='media')

            # new code
            resized_image_thumb.name = myfile1.name

            thumbFileFilter = Articles2.objects.filter(id=event_id).values('profile_image')
            thumbFilterFileName = thumbFileFilter[0]['profile_image']
            # thumbFilterFileLoc = os.path.join(BASE_DIR, thumbFilterFileName)
            if (thumbFilterFileName != '' and thumbFilterFileName != None):
                thumbFilterFileLoc = BASE_DIR+thumbFilterFileName
                if os.path.exists(thumbFilterFileLoc):
                    os.remove(thumbFilterFileLoc)

            # if os.path.exists(MEDIA_DIR + "/" + myfile1.name):
            #      os.remove(MEDIA_DIR + "/" + myfile1.name)
            resized_image_thumb.save(MEDIA_DIR + "/" + resized_image_thumb.name, format='PNG')
            filename_1 = resized_image_thumb.name
            # logging.debug(filename)
            uploadedfileurl_1 = fs_1.url(filename_1)
            u_p = uploadedfileurl_1
            Articles2.objects.filter(id=event_id).update(profile_image=u_p)
            ######### ends here ~ new code 


        myfile2 = request.POST.get('myfile2', None)

        print(myfile2)
        uploadedfileurl_2 = ''
        u_editables = ''
        if request.method == 'POST' and request.FILES.get('myfile2', None):
            myfile2 = request.FILES['myfile2']
            editable_name = image_name + '-' + 'editable' + \
                '.' + myfile2.name.split('.')[-1]
            print(editable_name)
            myfile2.name = editable_name
            fs_2 = FileSystemStorage(location='media/editables')
            

            editableFileFilter = Articles2.objects.filter(id=event_id).values('editable_image')
            editableFilterFileName = editableFileFilter[0]['editable_image']
            # editableFilterFileLoc = os.path.join(BASE_DIR, editableFilterFileName)
            if (editableFilterFileName != '' and editableFilterFileName != None):
                editableFilterFileLoc = BASE_DIR+editableFilterFileName
                if os.path.exists(editableFilterFileLoc):
                    os.remove(editableFilterFileLoc)

            # if os.path.exists(MEDIA_DIR + "/editables/" + myfile2.name):
            #     os.remove(MEDIA_DIR + "/editables/" + myfile2.name)
            filename2 = fs_2.save(myfile2.name, myfile2)
            uploadedfileurl_2 = fs_2.url(filename2)
            u_editables = uploadedfileurl_2
            u_editables = uploadedfileurl_2.replace("/media/", "/media/editables/")
            Articles2.objects.filter(id=event_id).update(editable_image=u_editables)
        # articles2.banner = u_banner
        # articles2.profile_image = u_p
        # articles2.editable_image = u_editables
        # s=Articles2(id=event_id,banner=u_banner,profile_image=u_p,editable_image=u_editables)

        # print(s)
        # articles2.save()



        # return redirect(base_url)
        return redirect(reverse('dashboard:edit-event-three', args={event_id}))

    return render(request, 'dashboard/edit_event_three.html', {'pro_image': pro_image, 'banner': banner, 'edit_image':edit_image})
# ends here ~ code for edit images step 3 on edit event mode


# def unlock_rsvp(request, event_id, table_id_par):
#     if request.method == 'GET':
#         filterFinanceStdChrge = FinanceStandardCharges.objects.filter(service_type="unlock_rsvp").values()
#         financeStdChrgeList = list(filterFinanceStdChrge)
#         print(' >>>>>>>>>>>.......>>>>>>>......>>>>>>>.. ',financeStdChrgeList)
#         return render(request, 'dashboard/unlock-rsvp.html',{'packageList':financeStdChrgeList})
#     else:
#         return render(request, 'dashboard/unlock-rsvp.html')


######################################


# @csrf_exempt
# def unlock_rsvp(request, event_id, table_id_par):
#     try:  
#         # Get Premium Packages list (only unlock_rsvp) from Finance Standard Charges DB
#         filterFinanceStdChrge = FinanceStandardCharges.objects.filter(service_type="unlock_rsvp").values()
#         financeStdChrgeList = list(filterFinanceStdChrge)
#         # ends here ~ Get Premium Packages list (only unlock_rsvp) from Finance Standard Charges DB
        
#         return render(request, "dashboard/unlock-rsvp.html", {'packageList':financeStdChrgeList, 'event_id':event_id, 'table_id':table_id_par})        
#     except Exception as e:
#         print('error  in unlock_rsvp function >> ',e)


# def subscribe_premium_package(request, event_id, table_id_par, charges_id_par):

#     # query for filter data from different table to get organizer email
#     filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=event_id).values('connected_user')
#     connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']
#     ##############################################

#     # check bank details (if bank details exists then continue otherwise redirect to bank details page)
#     filterBankDetails = BankDetails.objects.filter(user_id=connectedUserId)
#     if not filterBankDetails:
#         return redirect('/live/dashboard/bank-details')
#     # ends here ~ check bank details (if bank details exists then continue otherwise redirect to bank details page)


#     ##############################################
#     filterUserData = Users.objects.get(id = connectedUserId)
#     organizerEmail = filterUserData.user
#     # ends here ~ query for filter data from different table to get organizer email

#     # fetch current package plan on bases on charges_id_par
#     filterFinanceStdChrge = FinanceStandardCharges.objects.filter(charges_id=charges_id_par).values()
#     listFinanceStdChrge = list(filterFinanceStdChrge)
#     dictFinanceStdChrge = listFinanceStdChrge[0]
    
#     # ends here ~ fetch current package plan on bases on charges_id_par


#     data = {}
#     extra_info = {}
#     txnid = get_transaction_id()
    



#     packageCharge = float(dictFinanceStdChrge['fee'])
#     tax_value_num = dictFinanceStdChrge['tax_value'].split('%')[0]
#     tax_value_num = float(tax_value_num)
#     packageChrgeTaxAmt = (packageCharge/100)*tax_value_num
#     packageChrgeAfterTax = packageCharge + packageChrgeTaxAmt
#     extra_info['tax_name'] = dictFinanceStdChrge['tax_name']
#     extra_info['tax_value'] = dictFinanceStdChrge['tax_value']
#     extra_info['packageChargeBeforeTax'] = packageCharge

#     hash_ = generate_hash(request, txnid, packageChrgeAfterTax, dictFinanceStdChrge['service_type'], filterUserData.firstname, organizerEmail,event_id, table_id_par, charges_id_par)
#     hash_string = get_hash_string(request, txnid, packageChrgeAfterTax, dictFinanceStdChrge['service_type'], filterUserData.firstname, organizerEmail, event_id, table_id_par, charges_id_par)

#     # use constants file to store constant values.
#     # use test URL for testing
#     data["action"] = conf_settings.PAYU_PAYMENT_URL 
#     data["amount"] = packageChrgeAfterTax
#     data["productinfo"]  = dictFinanceStdChrge['service_type']
#     data["key"] = conf_settings.PAYU_MERCHANT_KEY
#     data["txnid"] = txnid
#     data["hash"] = hash_
#     data["hash_string"] = hash_string
#     data["firstname"] = filterUserData.firstname
#     data["email"] = organizerEmail
#     data["phone"] = filterUserData.mobile
#     data["service_provider"] = conf_settings.SERVICE_PROVIDER 
#     data["udf1"] = str(event_id) #USING UDF1 for event_id
#     data["udf2"] = str(table_id_par) #USING UDF2 for table_id (rsvp table)
#     data["udf3"] = str(charges_id_par) #USING UDF3 for charges_id (FinanceStandardCharges table)
#     data["furl"] = request.build_absolute_uri(reverse("dashboard:payment-fail-rsvp"))
#     data["surl"] = request.build_absolute_uri(reverse("dashboard:payment-success-rsvp"))
#     # data["surl"] = request.build_absolute_uri(reverse("students:payment_success"))
    


#     return render(request, "dashboard/subscribe_premium_package.html", {'event_id':event_id, 'table_id':table_id_par, 'data':data, 'extra_info':extra_info})     
    
# # generate the hash
# def generate_hash(request, txnid, packageAmtPar, packageInfoPar, firstnamePar, emailPar, udf1par, udf2par, udf3par):
#     try:
#         # get keys and SALT from dashboard once account is created.
#         # hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
#         hash_string = get_hash_string(request,txnid, packageAmtPar, packageInfoPar, firstnamePar, emailPar, udf1par, udf2par, udf3par)
#         generated_hash = hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()
#         return generated_hash
#     except Exception as e:
#         # log the error here.
#         logging.getLogger("error_logger").error(traceback.format_exc())
#         return None

# # create hash string using all the fields
# def get_hash_string(request, txnid, packageAmtPar, packageInfoPar, firstnamePar, emailPar, udf1par, udf2par, udf3par):
#     hash_string = conf_settings.PAYU_MERCHANT_KEY+"|"+txnid+"|"+str(float(packageAmtPar))+"|"+packageInfoPar+"|"
#     hash_string += firstnamePar+"|"+emailPar+"|"
#     hash_string += str(udf1par)+"|"+str(udf2par)+"|"+str(udf3par)+"|"
#     hash_string += "|||||||"+conf_settings.PAYU_MERCHANT_SALT

#     return hash_string

# # generate a random transaction Id.
# def get_transaction_id():
#     hash_object = hashlib.sha256(str(randint(0,9999)).encode("utf-8"))
#     # take approprite length
#     txnid = hash_object.hexdigest().lower()[0:32]
#     return txnid


# # no csrf token require to go to Success page. 
# # This page displays the success/confirmation message to user indicating the completion of transaction.
# @csrf_exempt
# def payment_success_rsvp(request):
#     ###################NOTE#####################
#     #USE UDF1 for event_id
#     #USE UDF2 for table_id (rsvp table)
#     #USE UDF3 for charges_id (FinanceStandardCharges table)
#     ##############ENDS NOTE#####################
   
   
#     payUresp = dict(request.POST)
#     eventId = payUresp['udf1'][0]
#     rsvp_table_id = payUresp['udf2'][0]

#     # query for get user id and email
#     filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=eventId).values('connected_user')
#     connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']

#     filterUserData = Users.objects.get(id = connectedUserId)
#     organizerEmail = filterUserData.user
#     organizerName = filterUserData.firstname
#     # ends here ~ query for get user id and email

    
#     purchaseDate = payUresp['addedon'][0]
#     bookingId = payUresp['payuMoneyId'][0]
#     pricePaid = payUresp['amount'][0]
#     finance_charges_id = payUresp['udf3'][0] # use for package_brought

#     # store required values in package sales
#     filterPackageSales = PackageSales.objects.aggregate(Max('invoice_number'))
#     invoiceNumberMax = filterPackageSales['invoice_number__max']
#     if (invoiceNumberMax == None):
#         PackageSales.objects.create(user_id=connectedUserId, purchase_date=purchaseDate, booking_id=bookingId, price_paid=pricePaid, package_bought=finance_charges_id, invoice_number=0)
#     else:
#         invoiceNumberMax+=1
#         PackageSales.objects.create(user_id=connectedUserId, purchase_date=purchaseDate, booking_id=bookingId, price_paid=pricePaid, package_bought=finance_charges_id, invoice_number=invoiceNumberMax)
#     # ends here ~ store required values in package sales

#     # update leads package on successful payment 
#     StatusPromotionTicketing.objects.filter(event_id=eventId).update(leads_package=finance_charges_id)
#     # ends here ~ update leads package on successful payment 

#     # data for template
#     filterArticles2 = Articles2.objects.get(id = eventId)
#     eventName = filterArticles2.event_name

    
#     filterFinanceStdChg = FinanceStandardCharges.objects.get(charges_id=finance_charges_id)
#     intialPkgPrice = filterFinanceStdChg.fee
#     intialPkgPrice = float(intialPkgPrice)
#     tax_value_num = filterFinanceStdChg.tax_value.split('%')[0]
#     tax_value_num = float(tax_value_num)
#     packageChrgeTaxAmt = (intialPkgPrice/100)*tax_value_num
#     packageTax = str(packageChrgeTaxAmt) + ' ('+filterFinanceStdChg.tax_value + ' ' + filterFinanceStdChg.tax_name+')'
#     # ends here ~ data for template

#     # send payment success email

#     subject = 'Congratulations! RSVPs for your '+ eventName+' are unlocked.'
#     email_from = conf_settings.EMAIL_HOST_USER
#     recipient_list = [organizerEmail]
#     html_message = render_to_string('static/common/rsvp-paymet-success.html', {
#         'event_name': eventName,
#         'organizer_name': organizerName,
#         'packge_price': intialPkgPrice,
#         'packge_tax': packageTax,
#         'total': pricePaid,
#         'amount_paid': pricePaid,
#         'order_id': bookingId,
#         'packge_name':'Unlock RSVP'
#     })
#     msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
#     msg.content_subtype = "html"
#     msg.send(fail_silently=False)

#     # ends here ~ send payment success mail

#     ##################################################
#     ##################################################
#     #############FOR INVOICE DETAILS##################
#     ##################################################
#     ##################################################

#     # get bank details
#     filerBankDetails = BankDetails.objects.get(user_id=connectedUserId)
#     clientGstNumber = filerBankDetails.gst_number
#     # ends here ~ get bank details

#     # generate pdf for invoice
    
#     rsvp_invoice_name = str(uuid.uuid4())+ '_'+str(connectedUserId)+'_'+str(invoiceNumberMax)
#     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     MEDIA_DIR = os.path.join(BASE_DIR, 'media/rsvp_invoice')
#     finalInvoiceName = MEDIA_DIR + "/" + rsvp_invoice_name + '.pdf'
   
#     html_string = render_to_string('static/common/rsvp-invoice.html', {
#         'event_name': eventName,
#         'organizer_name': organizerName,
#         'packge_price': intialPkgPrice,
#         'packge_tax': packageTax,
#         'total': pricePaid,
#         'amount_paid': pricePaid,
#         'order_id': bookingId,
#         'product_name':'Unlock RSVP',
#         'client_gst_number':clientGstNumber,
#         'invoice_number':invoiceNumberMax,
#         'invoice_date':purchaseDate
#     })
#     HTML(string=html_string).write_pdf(finalInvoiceName)
#     invoicePdfFile = open(finalInvoiceName, 'rb')

#     # ends here ~ generate pdf for invoice

#     # send invoice email

#     subject = 'Invoice Details'+ ' '+str(eventName)
#     email_from = conf_settings.EMAIL_HOST_USER
#     recipient_list = [organizerEmail]
#     html_message = 'Hi, Please check attachment file for invoice PDF'
#     msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
#     msg.attach('Unlock RSVP Invoice Details', invoicePdfFile.read(), 'application/pdf')
#     msg.content_subtype = "html"
#     msg.send(fail_silently=False)
#     invoicePdfFile.close()
#     # ends here ~ send invoice email

#     ##################################################
#     ##################################################
#     ########UNLOCK ALL RSVP FOR THIS EVENT############
#     ##################################################
#     ##################################################
#     # unlock all rsvp for this event
#     Rsvp.objects.filter(event_id=eventId).update(locked=0)
#     # ends here ~ unlock all rsvp for this event

#     return render(request, 'static/common/rsvp-paymet-success.html', {'event_name': eventName,'organizer_name': organizerName,'packge_price': intialPkgPrice,'packge_tax': packageTax,'total': pricePaid,'amount_paid': pricePaid,'order_id': bookingId,'packge_name':'Unlock RSVP'})

# # no csrf token require to go to Failure page. This page displays the message and reason of failure.
# @csrf_exempt
# def payment_fail_rsvp(request):
#     try:
#         ###################NOTE#####################
#         #USE UDF1 for event_id
#         #USE UDF2 for table_id (rsvp table)
#         #USE UDF3 for charges_id (FinanceStandardCharges table)
#         ##############ENDS NOTE#####################
       
       
#         payUresp = dict(request.POST)
#         eventId = payUresp['udf1'][0]
#         rsvp_table_id = payUresp['udf2'][0]

#         # query for get user id and email
#         filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=eventId).values('connected_user')
#         connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']

#         filterUserData = Users.objects.get(id = connectedUserId)
#         organizerEmail = filterUserData.user
#         organizerName = filterUserData.firstname
#         # ends here ~ query for get user id and email

#         # get required data from Articles2 Table
#         filterArticles2 = Articles2.objects.get(id = eventId)
#         eventName = filterArticles2.event_name
#         # ends here ~ get required data from Articles2 Table

#         amountFailed = payUresp['amount'][0]
#         failedTransactionDate = payUresp['addedon'][0]


#         try_again_url = 'http://'+request.get_host()+'/live/dashboard/unlock-rsvp/'+str(eventId)+'/'+str(rsvp_table_id)

#         # send email to organizer on payment failed
#         subject = 'Oops! yur purchase for '+ eventName+' was failed.'
#         email_from = conf_settings.EMAIL_HOST_USER
#         recipient_list = [organizerEmail]
#         html_message = render_to_string('static/common/rsvp-payment-failure.html', {
#             'event_name': eventName,
#             'organizer_name': organizerName,
#             'packge_name':'Unlock RSVP ~ '+amountFailed,
#             'try_again_url':try_again_url
#         })
#         msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
#         msg.content_subtype = "html"
#         msg.send(fail_silently=False)
#         # ends here ~ send email to organizer on payment failed

#         # send email to admin on payment failed for follow up
#         subject = 'Email for Follow up on RSVP Payment Failed ~ '+organizerEmail
#         email_from = conf_settings.EMAIL_HOST_USER
#         recipient_list = ['vishal@ercess.com']
#         html_message = render_to_string('static/common/rsvp-payment-failure-admin.html', {
#             'event_name': eventName,
#             'organizer_name': organizerName,
#             'packge_name':'Unlock RSVP ~ '+amountFailed,
#             'organizer_email':organizerEmail,
#             'transaction_date':failedTransactionDate,
#             'amount_failed':amountFailed,
#             'organizer_id':connectedUserId
#         })
#         msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
#         msg.content_subtype = "html"
#         msg.send(fail_silently=False)
#         # ends here ~ send email to admin on payment failed for follow up


#         return render(request, 'static/common/rsvp-payment-failure.html', {
#             'event_name': eventName,
#             'organizer_name': organizerName,
#             'packge_name':'Unlock RSVP ~ '+amountFailed,
#             'try_again_url':try_again_url
#         })
#     except Exception as e:
#         print('error in payment_fail_rsvp function >> ',e)


################DUPLICATE EVENTS STEP 1###################
def duplicate_event_basics(request, event_id):
    try:

        if 'userid' not in request.session.keys():
                return redirect('/live/login')

        s = []
        now = datetime.now()
        d = Articles2.objects.all().filter(id=event_id)
        if len(d) == 0:
            return redirect('/live/dashboard/organizer_dashboard')

        spe = StatusPromotionTicketing.objects.all().filter(
            event_id=event_id).values('approval')

        spea = spe[0]['approval']
        print(spea)
        if spea == 1:
            print("logs will be maintained")
        if d.values('event_name').count() > 0:
            s.append(d.values('event_name')[0]['event_name'])
        if d.values('website').count() > 0:
            s.append(d.values('website')[0]['website'])

        k = d.values('sdate')[0]['sdate']
        sl = now.replace(hour=k.hour, minute=k.minute, second=k.second,
                         microsecond=k.microsecond, year=k.year, month=k.month, day=k.day)
        # sd=datetime.date(k)
        print(sl)
        if k.month < 10:
            if k.day < 10:
                sda = '0' + str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
            else:
                sda = str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
        else:
            if k.day < 10:
                sda = '0' + str(k.day) + '/' + str(k.month) + '/' + str(k.year)
            else:
                sda = str(k.day) + '/' + str(k.month) + '/' + str(k.year)
        s.append(sda)
        s.append(d.values('start_time')[0]['start_time'])
        k1 = d.values('edate')[0]['edate']
        el = now.replace(hour=k1.hour, minute=k1.minute, second=k1.second,
                         microsecond=k1.microsecond, year=k1.year, month=k1.month, day=k1.day)

        # ed=datetime.date(k1)
        # print(ed)
        if k1.month < 10:
            if k1.day < 10:
                eda = '0' + str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
            else:
                eda = str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
        else:
            if k1.day < 10:
                eda = '0' + str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
            else:
                eda = str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
        print(eda)
        s.append(eda)
        s.append(d.values('end_time')[0]['end_time'])
        s.append(d.values('address_line1')[0]['address_line1'])
        s.append(d.values('address_line2')[0]['address_line2'])
        s.append(d.values('city')[0]['city'])
        s.append(d.values('state')[0]['state'])
        s.append(d.values('country')[0]['country'])
        s.append(d.values('pincode')[0]['pincode'])
        s.append(d.values('webinar_link')[0]['webinar_link'])
        try:
            s.append(float(d.values('latitude')[0]['latitude']))
        except:
            pass

        try:
            s.append(float(d.values('longitude')[0]['longitude']))
        except:
            pass

        s.append(d.values('place_id')[0]['place_id'])
        # s.append(d.values('venue_not_decided')[0]['venue_not_decided'])
        print(s[1])
        par = ['event_name', 'website', 'sdate', 'start_time', 'eddate', 'end_time', 'address_line1',
               'address_line2', 'city', 'state', 'country', 'pincode', 'latitude', 'longitude', 'place_id']

        if request.method == 'POST':
            # @author Shubham ~ new code to check duplicate and return an error message to UI
            oldEventId = event_id
            requestData = request.POST
            reqEventName = requestData['event_name']
            reqStartDate = datetime.strptime(requestData['sdate'],'%d/%m/%Y')
            reqEndDate = datetime.strptime(requestData['edate'],'%d/%m/%Y')
            if requestData.get('webinar_link'):
                fAddress = ''
            else:
                fAddress = requestData['address_line1']+ "," + str(requestData['address_line2'])+ "," + requestData['state'] + "," + requestData['city'] + "," + str(requestData['pincode'])
            filterArticleData = Articles2.objects.filter(sdate=reqStartDate,edate=reqEndDate,full_address=fAddress,event_name=reqEventName)
            if len(filterArticleData) == 1:
                return render(request, 'dashboard/duplicate_event_step_1.html', {'event_id': event_id, 's': s, 'errorMessage':'This event already exists'})
                # return HttpResponse({'errorMessage':'Duplicate Events Cannot be Created'})
            # ends here ~ @author Shubham ~ new code to check duplicate and return an error message to UI
            #######################contact#########################
            user = Users.objects.get(pk=request.session['userid'])
            print('\n\n\n\n\n\n',user.mobile)
            if user.mobile == '' or user.mobile == 0 or user.mobile == None:
                return redirect('dashboard:updateContact')

            #######################################################

            event_md5 = md5(request.POST.get('event_name').encode('utf-8')).hexdigest()[:34]
            print(event_md5)
            print("Up postttttttttttttttttt")
            context = {'md5' : event_md5}
            event_name=request.POST.get('event_name')
            print(event_name)
            # l.append(event_name)
            serializer = Articles2Serializer(data=request.POST, context=context)
            if not serializer.is_valid():
                return Response({'serializer': serializer,'flag':True,'event_name':event_name})
            print(serializer)
            print("posttttttttttttttttttttttttt")
            obj = serializer.save()

            if requestData.get('webinar_link'):
                obj.full_address = ''
            else:
                venue_not_decided = request.POST.get('venue_not_decided');
                if venue_not_decided == 'true':
                    obj.venue_not_decided = True
                    obj.full_address = ''
                else:
                    obj.venue_not_decided = False
                    obj.full_address = obj.address_line1+ "," + str(obj.address_line2)+ "," + obj.state + "," + obj.city + "," + str(obj.pincode)

            event_id = obj.id
            obj.save()
            #user_id = request.user.id
            user_id = request.session.get('userid')
            unique_id = f'EL{event_id}'
            data = {'event_id':event_id, 'unique_id':unique_id,'mode':'created',
                    'private':0,'event_active':1,'approval':0, 'network_share':1,
                    'ticketing':0, 'promotion':0, 'connected_user':user_id, 'complete_details':0}

            serializer = StatusPromotionTicketingSerializer(data=data)
            if not serializer.is_valid():
                return Response({'serializer': serializer,'flag':True})
            serializer.save()
            messages.success(request, f'Thank you. Event has been registered. your event id is {event_id}')

            # code december 24 2019
            countryName = obj.country
            filterAboutContries = AboutCountries.objects.filter(country=countryName).values('default_sms_credits','default_email_credits')
            aboutCountriesList = list(filterAboutContries)
            if(len(filterAboutContries) > 0):
                aboutCountriesDict = aboutCountriesList[0]
                defaultSmsCredits = aboutCountriesDict['default_sms_credits']
                defaultEmailCredits = aboutCountriesDict['default_email_credits']
            else:
                defaultSmsCredits = 0
                defaultEmailCredits = 0
            # ends here ~ code december 24 2019

            # function for create short-url with different sources
            shortUrlSourcesList = ['organic', 'sms_marketing_organizer', 'sms_marketing_admin', 'email_marketing_organizer', 'email_marketing_admin', 'referral_marketing', 'social_organic', 'social_paid', 'organizer']
            createMultipleShortUrl(event_id,shortUrlSourcesList)
            # ends here ~ function for create short-url with different sources

            StatusPromotionTicketing.objects.filter(event_id=event_id).update(step1_complete = 1,referrer_program_status=1, sms_credit = int(defaultSmsCredits), email_credit = int(defaultEmailCredits))

            base_url = reverse('dashboard:duplicate-event-two', kwargs={'old_event_id':oldEventId, 'new_event_id':event_id})
            return redirect(base_url)

            return render(request, 'dashboard/duplicate_event_step_1.html', {'event_id': event_id, 's': l, })

        return render(request, 'dashboard/duplicate_event_step_1.html', {'event_id': event_id, 's': s, })
    except Exception as e:
        print('error in duplicate_event_basics >> ',e)


def duplicate_event_two(request, old_event_id, new_event_id):
    try:
        if 'userid' not in request.session.keys():
            return redirect('/live/login')

        if request.method ==  'GET':
            # cat = []
            # cat1 = []
            # a = Categories.objects.all().values('category')
            # # print(a)
            # for i in a:
            #     cat.append(i['category'])
            # a1 = Categories.objects.all().values('category_id')
            # # print(a1)
            # for i in a1:
            #     cat1.append(i['category_id'])
            # # print(cat1)
            # c = zip(cat, cat1)

            # @author Shubham ~ old code modified on december 27 2019
            cat = []
            cat1 = []
            a = Categories.objects.all().values('category','category_id')
            for i in a:
                cat.append(i['category'])
                cat1.append(i['category_id'])
            c = zip(cat, cat1)
            # ends here ~ @author Shubham ~ old code modified on december 27 2019

            e = CategorizedEvents.objects.all().filter(
                event_id=old_event_id).values('category_id')

            k = ''
            l = ''
            if e.values('category_id').count() > 0 and e.values('topic_id').count() > 0:
                k = e.values('category_id')[0]['category_id']
                l = e.values('topic_id')[0]['topic_id']
                print(type(k), l)

            # a2 = Topics.objects.all().filter(category=k).values('topic')
            # a3 = Topics.objects.all().filter(category=k).values('topics_id')
            # # print(a2,a3)
            # to = []
            # t_i = []
            # for i in range(0, len(a2)):
            #     to.append(a2[i]['topic'])
            #     t_i.append(a3[i]['topics_id'])
            # print(to, t_i)
            # t = zip(to, t_i)

            # modified code
            a2 = Topics.objects.all().filter(category=k).values('topic','topics_id')
            # print(a2,type(a3[0]['topics_id']))
            to = []
            t_i = []
            for i in range(0, len(a2)):
                to.append(a2[i]['topic'])
                t_i.append(a2[i]['topics_id'])
            print(to, t_i)
            t = zip(to, t_i)
            # ends here ~ modified code

            f = StatusPromotionTicketing.objects.all().filter(event_id=old_event_id)
            pr = f.values('private')[0]['private']
            tick = f.values('ticketing')[0]['ticketing']
            print(type(pr), tick)

            # get event name from articles 2 table
            articles2Filter = Articles2.objects.get(id=new_event_id)
            event_name = articles2Filter.event_name
            # ends here ~ get event name from articles 2 table

            return render(request, 'dashboard/duplicate_event_step_2.html', {'old_event_id': old_event_id,'new_event_id': new_event_id, 'c': c, 'k': k, 't': t, 'l': l, 'pr': pr, 'tick': tick, 'event_name':event_name})


        if request.method == 'POST':
            event_id = new_event_id
            context = {'event_id' : event_id}
            print(request.POST)
            serializer = CategorizedEventsSerializer(data=request.POST, context=context)
            if not serializer.is_valid():
                return Response({'serializer': serializer,'flag':True})
            serializer.save()
            print("----updated event tables")
            user_id = request.user.id
            if not user_id:
                user_id = 1
            unique_id = f'EL{event_id}'

            if request.POST.get('type1') == 'public':
                type_event = 0
            else:
                type_event = 1
            if request.POST.get('type2') == 'paid':
                ticketing = 1
            else:
                ticketing = 0
            data = {'private':type_event, 'ticketing':ticketing,}
            inst = get_object_or_404(StatusPromotionTicketing, event_id=event_id)
            print(inst)
            serializer = StatusPromotionTicketingSerializer(inst, data=data, partial=True)
            if not serializer.is_valid():
                return Response({'serializer': serializer,'flag':True})
            serializer.save()

            StatusPromotionTicketing.objects.filter(event_id=event_id).update(step1_complete = 1, step2_complete = 1)

            base_url = reverse('dashboard:duplicate-event-three', kwargs={'old_event_id':old_event_id, 'new_event_id':new_event_id})
            return redirect(base_url)


        
    except Exception as e:
        print('error in duplicate_event_two function >> ',e)


def duplicate_event_three(request, old_event_id, new_event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    if request.method == 'GET':
        try:
            article = Articles2.objects.get(id=old_event_id)
            pro_image= article.profile_image
            banner = article.banner
            edit_image = article.editable_image
            # get event name from articles 2 table
            articles2Filter = Articles2.objects.get(id=new_event_id)
            event_name = articles2Filter.event_name
            # ends here ~ get event name from articles 2 table
            return render(request, 'dashboard/duplicate_event_step_3.html', {'pro_image': pro_image, 'banner': banner, 'edit_image':edit_image, 'old_event_id':old_event_id, 'new_event_id':new_event_id, 'event_name':event_name})
        except Exception as e:
            print('error in duplicate_event_three function >> ',e)
            # return redirect('/live/dashboard/organizer_dashboard')
    if request.method == 'POST':
        # try:
        imageData = request.POST
        articles2 = Articles2.objects.get(id=new_event_id)
        event_name = re.sub('[^A-Za-z0-9 ]+', '', articles2.event_name)
        event_name = event_name.replace(' ', '-')
        image_name = event_name + '-' + str(new_event_id)
        print(image_name)
        uploadedfileurl = ''
        u_banner = ''

        bannerImgName = imageData['image0_name']
        thumbImgName = imageData['image1_name']
        editableImgName = imageData['image2_name']

        
        if request.method == 'POST' and request.FILES.get('myfile', None):
            print('==========1111111111111111111111111===========')
            myfile = request.FILES['myfile']
            # logging.debug('{}'.format(myfile))
            # logging.debug(myfile.name.split('.'))
            image_name_banner = image_name + '-' + \
                'banner' + '.' + myfile.name.split('.')[-1]
            # logging.debug(
                # 'banner image name will be saved as: {}'.format(image_name_banner))
            # logging.debug(image_name_banner)
            myfile.name = image_name_banner
            x_s = request.POST.get('x', '')
            y_s = request.POST.get('y', '')
            w_s = request.POST.get('width', '')
            h_s = request.POST.get('height', '')

            if(x_s == None or x_s == ''):
                x = 0
                y = 0
            else:
                x = float(x_s)
                y = float(y_s)
            w = float(w_s)
            h = float(h_s)


            image = Image.open(myfile)
            cropped_image = image.crop((x, y, w + x, h + y))
            # cropped_image = image.crop((x, y, w, h))
            # cropped_image = image.crop((0.0, 100.0, 800.0, 800.0))
            resized_image = cropped_image.resize((1600, 900), Image.ANTIALIAS)

            fs = FileSystemStorage(location='media')
            # logging.debug('File system storage data: {}'.format(fs))
            # # logging.debug(fs)
            # fs.save(myfile.name,resized_image)
            resized_image.name = myfile.name

            
            resized_image.convert('RGB').save(MEDIA_DIR + "/" + resized_image.name, format='PNG')
            filename = resized_image.name
            # logging.debug('final name: {}'.format(filename))
            # logging.debug(filename)
            uploadedfileurl = fs.url(filename)
            u_banner = uploadedfileurl
            Articles2.objects.filter(id=new_event_id).update(banner=u_banner)
        else:
            if (bannerImgName != '' and bannerImgName != None):
                
                bannerFileFilter = Articles2.objects.filter(id=old_event_id).values('banner')
                bannerFilterFileName = bannerFileFilter[0]['banner']
                if os.path.exists(BASE_DIR+bannerFilterFileName):
                    bannerNewFileName = bannerFilterFileName
                    bannerNewFileName = bannerNewFileName.split('/media/')[1]
                    bannerNewFileName = str(new_event_id)+bannerNewFileName

                    # bannerFilterFileLoc = os.path.join(BASE_DIR, bannerFilterFileName)
                    bannerFilterFileLoc = BASE_DIR+bannerFilterFileName
                    bannerNewFileLoc = BASE_DIR+'/media/'+bannerNewFileName

                    shutil.copy(bannerFilterFileLoc,bannerNewFileLoc)

                    # imgFile = Image.open(bannerFilterFileLoc)
                    # fs_1 = FileSystemStorage(location='media')
                    # fs_1.save(bannerNewFileName, imgFile)

                    Articles2.objects.filter(id=new_event_id).update(banner='/media/'+bannerNewFileName)
        # logging.debug(u_banner)
        # logging.debug('Saved url in db: {}'.format(u_banner))

        myfile1 = request.POST.get('myfile1', None)

        print(myfile1)
        uploadedfileurl_1 = ''
        u_p = ''
        if request.method == 'POST' and request.FILES.get('myfile1', None):
            # print('==========2222222222222222222222===========')
            # myfile1 = request.FILES['myfile1']
            # image_name_thumb = image_name + '-' + \
            #     'thumbnail' + '.' + myfile1.name.split('.')[-1]
            # print(image_name_thumb)
            # myfile1.name = image_name_thumb
            # fs_1 = FileSystemStorage(location='media')
            # print(myfile1.name, myfile1)
            
            # filename_1 = fs_1.save(myfile1.name, myfile1)
            # uploadedfileurl_1 = fs_1.url(filename_1)
            # u_p = uploadedfileurl_1
            # Articles2.objects.filter(id=new_event_id).update(profile_image=u_p)

            ######### new code
            myfile1 = request.FILES['myfile1']
            image_name_thumb = image_name + '-' + \
                'thumbnail' + '.' + myfile1.name.split('.')[-1]
            print(image_name_thumb)
            myfile1.name = image_name_thumb

            # new code
            x_s_thumb = request.POST.get('x_p', '')
            y_s_thumb = request.POST.get('y_p', '')
            w_s_thumb = request.POST.get('width_p', '')
            h_s_thumb = request.POST.get('height_p', '')

            if(x_s_thumb == None or x_s_thumb == ''):
                x_thumb = 0
                y_thumb = 0
            else:
                x_thumb = float(x_s_thumb)
                y_thumb = float(y_s_thumb)
            w_thumb = float(w_s_thumb)
            h_thumb = float(h_s_thumb)

            image = Image.open(myfile1)
            cropped_image = image.crop((x_thumb, y_thumb, w_thumb + x_thumb, h_thumb + y_thumb))
            resized_image_thumb = cropped_image.resize((1600, 900), Image.ANTIALIAS)
            resized_image_thumb.name = myfile1.name
            # ends here ~ new code

            fs_1 = FileSystemStorage(location='media')

            # if os.path.exists(MEDIA_DIR + "/" + myfile1.name):
            #      os.remove(MEDIA_DIR + "/" + myfile1.name)
            resized_image_thumb.save(MEDIA_DIR + "/" + resized_image_thumb.name, format='PNG')
            filename_1 = resized_image_thumb.name
            # logging.debug(filename)
            uploadedfileurl_1 = fs_1.url(filename_1)
            u_p = uploadedfileurl_1
            Articles2.objects.filter(id=new_event_id).update(profile_image=u_p)
            ######### ends here ~ new code 

        else:
            if (thumbImgName != '' and thumbImgName != None):
                
                thumbFileFilter = Articles2.objects.filter(id=old_event_id).values('profile_image')
                thumbFilterFileName = thumbFileFilter[0]['profile_image']
                if os.path.exists(BASE_DIR+thumbFilterFileName):
                    thumbNewFileName = thumbFilterFileName
                    thumbNewFileName = thumbNewFileName.split('/media/')[1]
                    thumbNewFileName = str(new_event_id)+thumbNewFileName

                    # thumbFilterFileLoc = os.path.join(BASE_DIR, thumbFilterFileName)
                    thumbFilterFileLoc = BASE_DIR+thumbFilterFileName
                    # thumbFilterFileLoc = BASE_DIR+thumbNewFileName
                    thumbNewFileLoc = BASE_DIR+'/media/'+thumbNewFileName
                    shutil.copy(thumbFilterFileLoc,thumbNewFileLoc)

                    # imgFile = Image.open(thumbFilterFileLoc)
                    # fs_1 = FileSystemStorage(location='media')
                    # fs_1.save(thumbNewFileName, imgFile)



                    Articles2.objects.filter(id=new_event_id).update(profile_image='/media/'+thumbNewFileName)


        myfile2 = request.POST.get('myfile2', None)

        print(myfile2)
        uploadedfileurl_2 = ''
        u_editables = ''
        if request.method == 'POST' and request.FILES.get('myfile2', None):
            print('==========333333333333333333333===========')
            myfile2 = request.FILES['myfile2']
            editable_name = image_name + '-' + 'editable' + \
                '.' + myfile2.name.split('.')[-1]
            print(editable_name)
            myfile2.name = editable_name
            fs_2 = FileSystemStorage(location='media/editables')
            
            filename2 = fs_2.save(myfile2.name, myfile2)
            uploadedfileurl_2 = fs_2.url(filename2)
            u_editables = uploadedfileurl_2
            u_editables = uploadedfileurl_2.replace("/media/", "/media/editables/")
            Articles2.objects.filter(id=new_event_id).update(editable_image=u_editables)
        else:
            if (editableImgName != '' and editableImgName != None):
                if ('/media/editables/' in editableImgName):
                
                    editableFileFilter = Articles2.objects.filter(id=old_event_id).values('editable_image')
                    editableFilterFileName = editableFileFilter[0]['editable_image']
                    if os.path.exists(BASE_DIR+editableFilterFileName):
                        editableNewFileName = editableFilterFileName
                        editableNewFileName = editableNewFileName.split('/media/editables/')[1]
                        editableNewFileName = str(new_event_id)+editableNewFileName

                        # editableFilterFileLoc = os.path.join(BASE_DIR, editableFilterFileName)
                        # editableFilterFileLoc = BASE_DIR+editableNewFileName
                        editableFilterFileLoc = BASE_DIR+editableFilterFileName
                        editableNewFileLoc = BASE_DIR+'/media/editables/'+thumbNewFileName
                        shutil.copy(editableFilterFileLoc,editableNewFileLoc)



                        # imgFile = Image.open(editableFilterFileLoc)
                        # fs_1 = FileSystemStorage(location='media/editables')
                        # fs_1.save(editableNewFileName, imgFile)

                        Articles2.objects.filter(id=new_event_id).update(profile_image='/media/editables/'+editableNewFileName)
            # Articles2.objects.filter(id=new_event_id).update(editable_image=imageData['image2_name'])
        StatusPromotionTicketing.objects.filter(event_id=new_event_id).update(step1_complete = 1, step2_complete = 1, step3_complete = 1)
        
        base_url = reverse('dashboard:duplicate-event-four', kwargs={'old_event_id':old_event_id, 'new_event_id':new_event_id})

        return redirect(base_url)

        # except Exception as e:
        #     print('error in duplicate_event_three function Post >> ',e)

def  duplicate_event_four(request, old_event_id, new_event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    
    now = datetime.now()
    descform = Articles2Form()
    a = Articles2.objects.all().filter(id=old_event_id).values('description')
    d = a[0]['description']
    inst = get_object_or_404(Articles2, id=old_event_id)
    qs_india = get_object_or_404(AboutCountries, country="India")
    bank_regex1 = qs_india.bank_regex1
    bank_regex2 = qs_india.bank_regex2
    spe = StatusPromotionTicketing.objects.all().filter(
        event_id=old_event_id).values('approval')
    spea = spe[0]['approval']

    # get event name from articles 2 table
    articles2Filter = Articles2.objects.get(id=new_event_id)
    event_name = articles2Filter.event_name
    # ends here ~ get event name from articles 2 table

    if request.method == 'GET':
        try:
            return render(request, 'dashboard/duplicate_event_step_4.html', {'old_event_id':old_event_id, 'new_event_id':new_event_id, 'descform': descform, 'd': d, 'bank_regex1': bank_regex1, 'bank_regex2': bank_regex2, 'event_name':event_name})
        except Exception as e:
            print('error in duplicate_event_four function >> ',e)

    if request.method == 'POST':
        try:
            descform = Articles2Form(
                request.POST, instance=get_object_or_404(Articles2, id=new_event_id))

            if not descform.is_valid():
                return render(request, 'dashboard/edit_event_four.html', {'descform': descform, 'flag': True})
            
            d1 = (descform.cleaned_data.get('description'))
            
            if spea == 1:
                log = EventEditLogs(old_data=d, new_data=d1, parameter="description", taken_action='update',event_id=new_event_id, last_updated=now, user_id=request.session['userid'], role='organizer')
                log.save()

            descform.save()

            statusPromoFilter = StatusPromotionTicketing.objects.get(event_id=new_event_id)
            if(statusPromoFilter.ticketing == 0):
                base_url = reverse('dashboard:duplicate-event-six', kwargs={'old_event_id':old_event_id, 'new_event_id':new_event_id})
                return redirect(base_url)

            ticketFilter = Tickets.objects.filter(event_id=old_event_id).values('tickets_id')
            ticketFilterList = list(ticketFilter)
            if len(ticketFilterList) > 0:
                ticket_id = ticketFilterList[0]['tickets_id']
                StatusPromotionTicketing.objects.filter(event_id=new_event_id).update(step1_complete = 1, step2_complete = 1, step3_complete = 1, step4_complete = 1)
                base_url = reverse('dashboard:duplicate-event-five', kwargs={'old_event_id':old_event_id, 'new_event_id':new_event_id, 'ticket_id':ticket_id})
                return redirect(base_url)
            else:
                StatusPromotionTicketing.objects.filter(event_id=new_event_id).update(step1_complete = 1, step2_complete = 1, step3_complete = 1, step4_complete = 1)
                base_url = reverse('dashboard:duplicate-new-ticket', kwargs={'old_event_id':old_event_id, 'new_event_id':new_event_id})
                return redirect(base_url)

        except Exception as e:
            print('error in duplicate_event_four Post function >> ',e)

##################WORKING CODE##############
# def duplicate_event_five(request, old_event_id, new_event_id, ticket_id):
#     if 'userid' not in request.session.keys():
#         return redirect('/live/login')
#     try:
#         now = datetime.now()
#         inst = get_object_or_404(Articles2, id=new_event_id)
#         date = inst.sdate.strftime('%m/%d/%Y')
#         sdate = inst.sdate.strftime('%d/%m/%Y')
#         edate = inst.edate.strftime('%d/%m/%Y')
#         eventStartTime = inst.start_time.strftime('%H:%M')
#         eventEndTime = inst.end_time.strftime('%H:%M')

#         spe = StatusPromotionTicketing.objects.all().filter(
#             event_id=old_event_id).values('approval')
#         spea = spe[0]['approval']
#         print(spea)
#         if spea == 1:
#             print("logs will be maintained")

#         allTicketsDetailFilter = Tickets.objects.filter(event_id=old_event_id).values()
#         ticketnames = []
#         ticketIds = []
#         for ticket_data in allTicketsDetailFilter:
#             ticketnames.append(ticket_data['ticket_name'])
#             ticketIds.append(ticket_data['tickets_id'])

#         d = Tickets.objects.all().filter(tickets_id=ticket_id)
#         print(d)
#         s = []
#         s.append(d.values('ticket_name')[0]['ticket_name'])

#         s.append(d.values('ticket_price')[0]['ticket_price'])
#         s.append(d.values('other_charges')[0]['other_charges'])
#         s.append(d.values('other_charges_type')[0]['other_charges_type'])
#         s.append(d.values('ticket_qty')[0]['ticket_qty'])
#         s.append(d.values('min_qty')[0]['min_qty'])
#         s.append(d.values('max_qty')[0]['max_qty'])
#         k = d.values('ticket_start_date')[0]['ticket_start_date']
#         sl = now.replace(hour=k.hour, minute=k.minute, second=k.second,
#                          microsecond=k.microsecond, year=k.year, month=k.month, day=k.day)
#         # sd=datetime.date(k)
#         print(sl)
#         if k.month < 10:
#             if k.day < 10:
#                 sda = '0' + str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
#             else:
#                 sda = str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
#         else:
#             if k.day < 10:
#                 sda = '0' + str(k.day) + '/' + str(k.month) + '/' + str(k.year)
#             else:
#                 sda = str(k.day) + '/' + str(k.month) + '/' + str(k.year)
#         s.append(sda)
#         print(sda)
#         q = datetime.time(k)
#         s.append(q)
#         # s.append(d.values('start_time')[0]['start_time'])
#         k1 = d.values('expiry_date')[0]['expiry_date']
#         el = now.replace(hour=k1.hour, minute=k1.minute, second=k1.second,
#                          microsecond=k1.microsecond, year=k1.year, month=k1.month, day=k1.day)

#         # ed=datetime.date(k1)
#         # print(ed)
#         if k1.month < 10:
#             if k1.day < 10:
#                 eda = '0' + str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
#             else:
#                 eda = str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
#         else:
#             if k1.day < 10:
#                 eda = '0' + str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
#             else:
#                 eda = str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
#         s.append(eda)
#         print(eda)
#         r = datetime.time(k1)
#         s.append(r)
#         print(r)
#         msg = d.values('ticket_msg')[0]['ticket_msg']
#         if msg == "None" or msg == "NULL" or msg == "" or msg == None:
#             msg = "1"
#         s.append(msg)
#         s.append(d.values('ticket_label')[0]['ticket_label'])

#         print(s)

#         if request.method == 'GET':
#             return render(request, 'dashboard/duplicate_event_step_5.html', {'old_event_id':old_event_id, 'new_event_id':new_event_id, 'event_id': new_event_id, 'ticket_id': ticket_id, 'event_start_date':date, 'sdate':sdate, 'edate':edate,'event_start_time':eventStartTime,'event_end_time':eventEndTime, 's': s, 'ticketnames':ticketnames,'ticketIds':ticketIds})
    
#     except Exception as e:
#         print('error in duplicate_event_five >> ',e)
############ENDS HERE WORKING DAY############

# common function for step 5 duplicate task
def duplicateStepFiveCommonFn(old_event_id, new_event_id, ticket_id):
    try:
        now = datetime.now()
        inst = get_object_or_404(Articles2, id=new_event_id)
        date = inst.sdate.strftime('%m/%d/%Y')
        sdate = inst.sdate.strftime('%d/%m/%Y')
        edate = inst.edate.strftime('%d/%m/%Y')
        eventStartTime = inst.start_time.strftime('%H:%M')
        eventEndTime = inst.end_time.strftime('%H:%M')

        spe = StatusPromotionTicketing.objects.all().filter(
            event_id=old_event_id).values('approval')
        spea = spe[0]['approval']
        print(spea)
        if spea == 1:
            print("logs will be maintained")

        allTicketsDetailFilter = Tickets.objects.filter(event_id=old_event_id).values()
        ticketnames = []
        ticketIds = []
        for ticket_data in allTicketsDetailFilter:
            ticketnames.append(ticket_data['ticket_name'])
            ticketIds.append(ticket_data['tickets_id'])

        d = Tickets.objects.all().filter(tickets_id=ticket_id)
        print(d)
        s = []
        s.append(d.values('ticket_name')[0]['ticket_name'])

        s.append(d.values('ticket_price')[0]['ticket_price'])
        s.append(d.values('other_charges')[0]['other_charges'])
        s.append(d.values('other_charges_type')[0]['other_charges_type'])
        s.append(d.values('ticket_qty')[0]['ticket_qty'])
        s.append(d.values('min_qty')[0]['min_qty'])
        s.append(d.values('max_qty')[0]['max_qty'])
        k = d.values('ticket_start_date')[0]['ticket_start_date']
        sl = now.replace(hour=k.hour, minute=k.minute, second=k.second,
                         microsecond=k.microsecond, year=k.year, month=k.month, day=k.day)
        # sd=datetime.date(k)
        print(sl)
        if k.month < 10:
            if k.day < 10:
                sda = '0' + str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
            else:
                sda = str(k.day) + '/0' + str(k.month) + '/' + str(k.year)
        else:
            if k.day < 10:
                sda = '0' + str(k.day) + '/' + str(k.month) + '/' + str(k.year)
            else:
                sda = str(k.day) + '/' + str(k.month) + '/' + str(k.year)
        s.append(sda)
        print(sda)
        q = datetime.time(k)
        s.append(q)
        # s.append(d.values('start_time')[0]['start_time'])
        k1 = d.values('expiry_date')[0]['expiry_date']
        el = now.replace(hour=k1.hour, minute=k1.minute, second=k1.second,
                         microsecond=k1.microsecond, year=k1.year, month=k1.month, day=k1.day)

        # ed=datetime.date(k1)
        # print(ed)
        if k1.month < 10:
            if k1.day < 10:
                eda = '0' + str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
            else:
                eda = str(k1.day) + '/0' + str(k1.month) + '/' + str(k1.year)
        else:
            if k1.day < 10:
                eda = '0' + str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
            else:
                eda = str(k1.day) + '/' + str(k1.month) + '/' + str(k1.year)
        s.append(eda)
        print(eda)
        r = datetime.time(k1)
        s.append(r)
        print(r)
        msg = d.values('ticket_msg')[0]['ticket_msg']
        if msg == "None" or msg == "NULL" or msg == "" or msg == None:
            msg = "1"
        s.append(msg)
        s.append(d.values('ticket_label')[0]['ticket_label'])

        print(s)
        duplicateStepFiveDict = {'event_start_date':date, 'sdate':sdate, 'edate':edate,'event_start_time':eventStartTime,'event_end_time':eventEndTime, 's': s, 'ticketnames':ticketnames,'ticketIds':ticketIds}
        print('duplicateStepFiveDict',duplicateStepFiveDict)
        return duplicateStepFiveDict
    except Exception as e:
        pass
# ends here ~ common function for step 5 duplicate task


# function for get data from duplicate event steps 5 for duplicate task
def duplicate_event_five(request, old_event_id, new_event_id, ticket_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    try:
        
        eventTicketDetailsResp =  duplicateStepFiveCommonFn(old_event_id, new_event_id, ticket_id)

        # get event name from articles 2 table
        articles2Filter = Articles2.objects.get(id=new_event_id)
        event_name = articles2Filter.event_name
        # ends here ~ get event name from articles 2 table

        eventTicketDetailsResp.update({'old_event_id':old_event_id, 'new_event_id':new_event_id, 'event_id': new_event_id, 'ticket_id': ticket_id, 'event_name':event_name})
        if request.method == 'GET':
            return render(request, 'dashboard/duplicate_event_step_5.html', eventTicketDetailsResp)
            # return render(request, 'dashboard/duplicate_event_step_5.html', {'old_event_id':old_event_id, 'new_event_id':new_event_id, 'event_id': new_event_id, 'ticket_id': ticket_id, 'event_start_date':date, 'sdate':sdate, 'edate':edate,'event_start_time':eventStartTime,'event_end_time':eventEndTime, 's': s, 'ticketnames':ticketnames,'ticketIds':ticketIds})
    
    except Exception as e:
        print('error in duplicate_event_five >> ',e)
# ends here ~ function for get data from duplicate event steps 5 for duplicate task


# function for  duplicate event steps 5 in create mode
def duplicate_new_ticket(request, old_event_id, new_event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    try:
        event_id = new_event_id
        inst = get_object_or_404(Articles2, id=event_id)
        date = inst.sdate.strftime('%m/%d/%Y')
        sdate = inst.sdate.strftime('%d/%m/%Y')
        edate = inst.edate.strftime('%d/%m/%Y')
        eventStartTime = inst.start_time.strftime('%H:%M')
        eventEndTime = inst.end_time.strftime('%H:%M')

        aboutcountries = AboutCountries.objects.all()
        now = datetime.now()

        # get event name from articles 2 table
        articles2Filter = Articles2.objects.get(id=event_id)
        event_name = articles2Filter.event_name
        # ends here ~ get event name from articles 2 table

        return render(request, 'dashboard/duplicate_step_5_new_ticket.html', {'event_id': event_id, 'a': aboutcountries,'event_start_date':date, 'sdate':sdate, 'edate':edate,'event_start_time':eventStartTime,'event_end_time':eventEndTime,'old_event_id':old_event_id, 'new_event_id':new_event_id, 'event_name':event_name})
    except Exception as e:
        pass
# ends here ~ function for  duplicate event steps 5 in create mode

# save duplicate event five
@csrf_exempt
def save_duplicate_event_five(request):
    try:
        if 'userid' not in request.session.keys():
            return redirect('/live/login')

        if request.method == 'POST':
            requestData = request.POST

            now = datetime.now()
            ticket_id = requestData['ticket_id']
            ticketMode = requestData['ticket_mode']
            print(ticketMode == "createTkt",' >>>>>>>>>>>>>>>>>>>>>>>>>>>> ',ticketMode)
            event_id = requestData['event_id']

            # t = Tickets.objects.get(tickets_id=ticket_id)
            ticket_name = request.POST.get('ticket_name', '')
            ticket_price = request.POST.get('ticket_price', '')
            other_charges = request.POST.get('other_charges', '')
            other_charges_type = request.POST.get('other_charges_type', '')
            ticket_qty = request.POST.get('ticket_qty', '')
            min_qty = request.POST.get('min_qty', '')
            max_qty = request.POST.get('max_qty', '')

            tsd = request.POST.get('start_date')
            start_t = request.POST.get('start_time_step5')

            if start_t[0] == '1' and start_t[1] != ':':
                if start_t[6:] == 'AM' and start_t[:2] != '12':
                    start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                        start_t[3:5]), second=0, microsecond=0)
                elif start_t[6:] == 'AM' and start_t[:2] == '12':
                    # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                    start_time = now.time().replace(hour=0, minute=int(
                        start_t[3:5]), second=0, microsecond=0)
                elif start_t[6:] == 'PM' and start_t[:2] == '12':
                    start_time = now.time().replace(hour=int(start_t[:2]), minute=int(
                        start_t[3:5]), second=0, microsecond=0)
                else:
                    start_time = now.time().replace(
                        hour=(int(start_t[:2]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
            else:
                if start_t[5:] == 'AM':
                    start_time = now.time().replace(hour=int(start_t[0]), minute=int(
                        start_t[2:4]), second=0, microsecond=0)
                else:
                    start_time = now.time().replace(
                        hour=(int(start_t[0]) + 12), minute=int(start_t[2:4]), second=0, microsecond=0)

            st = str(start_time)
            sd = request.POST.get('end_date')
            end_t = request.POST.get('end_time_step5')

            if end_t[0] == '1' and end_t[1] != ':':
                if end_t[6:] == 'AM' and end_t[:2] != '12':
                    end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                        end_t[3:5]), second=0, microsecond=0)
                elif end_t[6:] == 'AM' and end_t[:2] == '12':
                    # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                    end_time = now.time().replace(hour=0, minute=int(
                        end_t[3:5]), second=0, microsecond=0)
                elif end_t[6:] == 'PM' and end_t[:2] == '12':
                    end_time = now.time().replace(hour=int(end_t[:2]), minute=int(
                        end_t[3:5]), second=0, microsecond=0)
                else:
                    end_time = now.time().replace(
                        hour=(int(end_t[:2]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
            else:
                if end_t[5:] == 'AM':
                    end_time = now.time().replace(hour=int(end_t[0]), minute=int(
                        end_t[2:4]), second=0, microsecond=0)
                else:
                    end_time = now.time().replace(
                        hour=(int(end_t[0]) + 12), minute=int(end_t[2:4]), second=0, microsecond=0)

            o = str(end_time)
            print(tsd + st)
            ticket_start_date = tsd + " " + st
            ticket_start_date = datetime.strptime(
                ticket_start_date, '%d/%m/%Y %H:%M:%S')
            expiry_date = sd + " " + o
            expiry_date = datetime.strptime(expiry_date, '%d/%m/%Y %H:%M:%S')
            print(ticket_start_date, expiry_date)

            ticket_msg = request.POST.get('ticket_msg', '')
            ticket_label = request.POST.get('ticket_label', '')

            if(ticketMode == "createTkt"):
                print('1111111111111111111111111111111111111111111111111111111')
                ticketSave = Tickets.objects.create(ticket_name = ticket_name,ticket_price = ticket_price,other_charges = other_charges,other_charges_type = other_charges_type,ticket_qty = ticket_qty,min_qty = min_qty,max_qty = max_qty,ticket_start_date = ticket_start_date,expiry_date = expiry_date,ticket_msg = ticket_msg,ticket_label = ticket_label,event_id=event_id, qty_left = ticket_qty, ercess_fee= 1, transaction_fee = 1,active=1)
                # call function to create discount coupon on creation of ticket 
                createDiscountCoupon(ticketSave.ticket_price, ticketSave.tickets_id, event_id, expiry_date, ticket_start_date)
                # ends here ~ call function to create discount coupon on creation of ticket
                print('##############################################')
            elif(ticketMode == "editTkt"):
                print('2222222222222222222222222222222222222222222222222222222')
                ticketsFilter = Tickets.objects.filter(tickets_id=ticket_id, event_id=event_id)
                if(len(ticketsFilter) != 0):
                    Tickets.objects.filter(tickets_id=ticket_id).update(ticket_name = ticket_name,ticket_price = ticket_price,other_charges = other_charges,other_charges_type = other_charges_type,ticket_qty = ticket_qty,min_qty = min_qty,max_qty = max_qty,ticket_start_date = ticket_start_date,expiry_date = expiry_date,ticket_msg = ticket_msg,ticket_label = ticket_label,event_id=event_id, qty_left = ticket_qty, ercess_fee= 1, transaction_fee = 1,active=1)
                else:
                    ticketSave = Tickets.objects.create(ticket_name = ticket_name,ticket_price = ticket_price,other_charges = other_charges,other_charges_type = other_charges_type,ticket_qty = ticket_qty,min_qty = min_qty,max_qty = max_qty,ticket_start_date = ticket_start_date,expiry_date = expiry_date,ticket_msg = ticket_msg,ticket_label = ticket_label,event_id=event_id, qty_left = ticket_qty, ercess_fee= 1, transaction_fee = 1,active=1)
                    # call function to create discount coupon on creation of ticket 
                    createDiscountCoupon(ticketSave.ticket_price, ticketSave.tickets_id, event_id, expiry_date, ticket_start_date)
                    # ends here ~ call function to create discount coupon on creation of ticket


            messageData = {'message':'Ticket Saved Successfully','responseType':'success', 'messageType':'success'}
            return HttpResponse(json.dumps(messageData))
    except Exception as e:
        print('error>>>',e)
# ends here ~ save duplicate event five

# duplicate step 6 (last step)
def  duplicate_event_six(request, old_event_id, new_event_id):
    if 'userid' not in request.session.keys():
        return redirect('/live/login')
    if request.method == 'GET':
        try:
            # @author Shubham ~ send email to user on loading of step 6 ~ October 14 2019

            # query for filter data from different table to get organizer email
            filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=new_event_id).values('connected_user')
            connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']

            # get event name from articles 2 table
            articles2Filter = Articles2.objects.get(id=new_event_id)
            event_name = articles2Filter.event_name
            # ends here ~ get event name from articles 2 table

            filterUserData = Users.objects.get(id = connectedUserId)
            organizerEmail = filterUserData.user
            # ends here ~ query for filter data from different table to get organizer email

            # filter and extract required data from Articles2 Table
            filterEventData = Articles2.objects.get(id = new_event_id)
            eventName = filterEventData.event_name
            # ends here ~ filter and extract required data from Articles2 Table

            # send email to organizer inside try except block
            try:
                subject = 'Congratulations! Your '+ eventName  +' is created on Ercess Live'
                email_from = conf_settings.EMAIL_HOST_USER
                recipient_list = [organizerEmail]
                html_message = render_to_string('static/common/event_created.html', {
                    'event_name': eventName,
                })

                msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
                msg.content_subtype = "html"
                msg.send(fail_silently=False)
            except Exception as e:
                print('error while send email to organizer >> ',e)

            try:
                subject = 'New Event is Created on Ercess Live'
                email_from = conf_settings.EMAIL_HOST_USER
                recipient_list = ['tickets@ercess.com']
                html_message = eventName + ' is created on Ercess Live.'
                msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
                msg.send()
            except Exception as e:
                print('error while send email to managers >> ',e)
            # ends here ~ send email to organizer inside try except block

            StatusPromotionTicketing.objects.filter(event_id=new_event_id).update(step1_complete = 1, step2_complete = 1, step3_complete = 1, step4_complete = 1, step5_complete = 1, complete_details=1)
            builder = AttendeeFormBuilder.objects.filter(event_id=old_event_id).values()
            builderListVal = list(builder)

            qs_types = AttendeeFormTypes.objects.values_list('type_id', 'name')
            qs_types_new = AttendeeFormTypes.objects.all().values()
            builder_list_final = []

            for builder_list in builderListVal:
                customQuestionDict = {'ques_title': '', 'ques_type': '', 'ques_accessibility':'', 'option_name':''}
                customQuestionDict['ques_title'] = builder_list['ques_title']
                customQuestionDict['ques_type'] = builder_list['ques_type']
                customQuestionDict['ques_accessibility'] = builder_list['ques_accessibility']
                optionName = AttendeeFormOptions.objects.filter(ques_id=builder_list['ques_id']).values('option_name')
                optionNameList = []
                if not optionName:
                    customQuestionDict['option_name'] = ''
                else:
                    for options in optionName:
                        optionNameList.append(options['option_name'])
                    optionNameListStr = str(optionNameList)[1:-1]
                    customQuestionDict['option_name'] = optionNameListStr

                builder_list_final.append(customQuestionDict.copy())

            return render(request, 'dashboard/duplicate_event_step_6.html',{'context':qs_types, 'builder_list_val':builder_list_final, 'qs_types_new':list(qs_types_new), 'event_name':event_name})
        except Exception as e:
            print('error in duplicate-event-six GET >> ',e)

    if request.method == 'POST':
        try:
            event_id = new_event_id

            for i,j in request.POST.items():
                if i not in ['csrfmiddlewaretoken']:
                    ques = request.POST.getlist(i)
                    type_inst = AttendeeFormTypes.objects.get(name=ques[2])
                    type_id=type_inst.type_id
                    add_que = AttendeeFormBuilder(event_id=event_id, ques_title=ques[1],
                                              ques_accessibility=int(ques[0]), ques_type=type_id)
                    add_que.save()
                    que_id = add_que.ques_id
                    if type_id == 5:
                        options = ques[-1].split(',')
                        for op in options:
                            add_op = AttendeeFormOptions(event_id=event_id, ques_id=que_id, option_name=op)
                            add_op.save()
            StatusPromotionTicketing.objects.filter(event_id=new_event_id).update(step1_complete = 1, step2_complete = 1, step3_complete = 1, step4_complete = 1, step5_complete = 1, step6_complete = 1)
            base_url = reverse('dashboard:event_added', args={new_event_id})
            return HttpResponse(base_url)
        except Exception as e:
            print('error in duplicate-event-six POST >> ',e)

# ends here ~ duplicate step 6 (last step)

# function to check is event already exits in db or not 
@csrf_exempt
def check_event_already_created(request):
    try:
        completeReqData = request.POST['completeData']
        completeReqJson = json.loads(completeReqData)

        requestData = completeReqJson
        reqEventName = requestData['event_name']
        reqStartDate = datetime.strptime(requestData['sdate'],'%d/%m/%Y')
        reqEndDate = datetime.strptime(requestData['edate'],'%d/%m/%Y')
        if requestData.get('webinar_link'):
            fAddress = ''
        else:
            fAddress = requestData['address_line1']+ "," + str(requestData['address_line2'])+ "," + requestData['state'] + "," + requestData['city'] + "," + str(requestData['pincode'])
        filterArticleData = Articles2.objects.filter(sdate=reqStartDate,edate=reqEndDate,full_address=fAddress,event_name=reqEventName)
        
        if len(filterArticleData) == 1:
            messageData = {'message':'This event already exists','responseType':'success', 'messageType':'error'}
        else:
            messageData = {'message':'no error.. submit form now..','responseType':'success', 'messageType':'success'}
        return HttpResponse(json.dumps(messageData))

    except Exception as e:
        print('error in check_event_already_created >> ',e)
# ends here ~ function to check is event already exits in db or not 


# function to check is event already exits in db or not (in edit mode)
@csrf_exempt
def check_event_already_created_edit(request):
    try:
        completeReqData = request.POST['completeData']
        completeReqJson = json.loads(completeReqData)

        requestData = completeReqJson
        reqEventName = requestData['event_name']
        reqEventId = requestData['event_id']
        reqStartDate = datetime.strptime(requestData['sdate'],'%d/%m/%Y')
        reqEndDate = datetime.strptime(requestData['edate'],'%d/%m/%Y')
        if requestData.get('webinar_link'):
            fAddress = ''
        else:
            fAddress = requestData['address_line1']+ "," + str(requestData['address_line2'])+ "," + requestData['state'] + "," + requestData['city'] + "," + str(requestData['pincode'])
        filterArticleData = Articles2.objects.filter(sdate=reqStartDate,edate=reqEndDate,full_address=fAddress,event_name=reqEventName).exclude(id=reqEventId)
        
        if len(filterArticleData) == 1:
            messageData = {'message':'Event is Already Created. Duplicate Event is not Allowed','responseType':'success', 'messageType':'error'}
        else:
            messageData = {'message':'no error.. submit form now..','responseType':'success', 'messageType':'success'}
        return HttpResponse(json.dumps(messageData))

    except Exception as e:
        print('error in check_event_already_created >> ',e)
# ends here ~ function to check is event already exits in db or not (in edit mode)

def case_studies(request):
    # print('inside how it works')
    return render(request, 'case-studies.html')

# get tickets on home duplicate task 
def duplicate_event_tickets(request, old_event_id, new_event_id):
    try:
        event_id = new_event_id
        id = []
        name = []
        price = []
        currency = []
        eventStartDate = []
        eventStart_date = ''

        country = Articles2.objects.all().filter(id=event_id).values('country')
        country = country[0]['country']
        print(country)
        currency = AboutCountries.objects.all().filter(
            country=country).values('currency')
        print(currency)
        if len(currency) != 0:
            currency = currency[0]['currency']
        print(currency)
        tick = Tickets.objects.all().filter(event_id=event_id)
        print('tick')
        print(list(tick))

        tktStartDate = []
        tktEndDate = []
        for i in range(0, len(tick)):
            print(i)
            id.append(tick.values('tickets_id')[i]['tickets_id'])
            name.append(tick.values('ticket_name')[i]['ticket_name'])
            price.append(tick.values('ticket_price')[i]['ticket_price'])
            tktStartDate.append(tick.values('ticket_start_date')[i]['ticket_start_date'])
            tktEndDate.append(tick.values('expiry_date')[i]['expiry_date'])

        eventStart_date = Articles2.objects.all().filter(id=event_id).values('sdate')
        eventStart_date = eventStart_date[0]['sdate']
        ticks = zip(id, name, price, tktStartDate, tktEndDate)

        # get event name from articles 2 table
        articles2Filter = Articles2.objects.get(id=new_event_id)
        event_name = articles2Filter.event_name
        # ends here ~ get event name from articles 2 table

        return render(request, 'dashboard/duplicate_step5_tkt_list.html', {'event_id': event_id, 'currency': currency, 'ticks': ticks, 'eventStart_date':eventStart_date, 'old_event_id':old_event_id, 'new_event_id':new_event_id, 'event_name':event_name})
    except Exception as e:
        pass
# ends here ~ get tickets on home duplicate task 

@csrf_exempt
def updateAnnAccessTable(request):
    try:
        requestData = request.POST
        announcementId = int(requestData['ann_id'])
        loginUserId = request.session['userid']
        print(announcementId,loginUserId)
        AnnouncementsAccess.objects.create(announcement_id=announcementId, user_id=loginUserId)
        messageData = {'message':'table updated','responseType':'success', 'messageType':'success'}
        return HttpResponse(json.dumps(messageData))
    except Exception as e:
        print('error in updateAnnAccessTable fn >> ', e)


###############################################################
######################## BUY PACKAGE OLD ######################
###############################################################


# def buy_premium_package(request, event_id, charges_id_par):

#     # query for filter data from different table to get organizer email
#     filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=event_id).values('connected_user')
#     connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']
#     ##############################################

#     # check bank details (if bank details exists then continue otherwise redirect to bank details page)
#     filterBankDetails = BankDetails.objects.filter(user_id=connectedUserId)
#     if not filterBankDetails:
#         return redirect('/live/dashboard/bank-details')
#     # ends here ~ check bank details (if bank details exists then continue otherwise redirect to bank details page)


#     ##############################################
#     filterUserData = Users.objects.get(id = connectedUserId)
#     organizerEmail = filterUserData.user
#     # ends here ~ query for filter data from different table to get organizer email

#     # fetch current package plan on bases on charges_id_par
#     filterFinanceStdChrge = FinanceStandardCharges.objects.filter(charges_id=charges_id_par).values()
#     listFinanceStdChrge = list(filterFinanceStdChrge)
#     dictFinanceStdChrge = listFinanceStdChrge[0]
    
#     # ends here ~ fetch current package plan on bases on charges_id_par


#     data = {}
#     extra_info = {}
#     txnid = get_transaction_id()

#     packageCharge = float(dictFinanceStdChrge['fee'])
#     tax_value_num = dictFinanceStdChrge['tax_value'].split('%')[0]
#     tax_value_num = float(tax_value_num)
#     packageChrgeTaxAmt = (packageCharge/100)*tax_value_num
#     packageChrgeAfterTax = packageCharge + packageChrgeTaxAmt
#     extra_info['tax_name'] = dictFinanceStdChrge['tax_name']
#     extra_info['tax_value'] = dictFinanceStdChrge['tax_value']
#     extra_info['packageChargeBeforeTax'] = packageCharge

#     serviceType = dictFinanceStdChrge['service_type']

#     hash_ = generateHash(request, txnid, packageChrgeAfterTax, dictFinanceStdChrge['service_type'], filterUserData.firstname, organizerEmail,event_id, charges_id_par)
#     hash_string = getHashString(request, txnid, packageChrgeAfterTax, dictFinanceStdChrge['service_type'], filterUserData.firstname, organizerEmail, event_id, charges_id_par)

#     # use constants file to store constant values.
#     # use test URL for testing
#     data["action"] = conf_settings.PAYU_PAYMENT_URL 
#     data["amount"] = packageChrgeAfterTax
#     data["productinfo"]  = dictFinanceStdChrge['service_type']
#     data["key"] = conf_settings.PAYU_MERCHANT_KEY
#     data["txnid"] = txnid
#     data["hash"] = hash_
#     data["hash_string"] = hash_string
#     data["firstname"] = filterUserData.firstname
#     data["email"] = organizerEmail
#     data["phone"] = filterUserData.mobile
#     data["service_provider"] = conf_settings.SERVICE_PROVIDER 
#     data["udf1"] = str(event_id) #USING UDF1 for event_id
#     data["udf2"] = str(charges_id_par) #USING UDF3 for charges_id (FinanceStandardCharges table)

#     if(serviceType == 'paid_marketing'):
#         data["furl"] = request.build_absolute_uri(reverse("dashboard:package-payment-fail"))
#         data["surl"] = request.build_absolute_uri(reverse("dashboard:package-payment-success"))
#     elif(serviceType == 'unlock_rsvp'):
#         data["furl"] = request.build_absolute_uri(reverse("dashboard:package-payment-fail"))
#         data["surl"] = request.build_absolute_uri(reverse("dashboard:package-payment-success"))
#     # data["surl"] = request.build_absolute_uri(reverse("students:payment_success"))
    

#     return render(request, "dashboard/buy_premium_package.html", {'event_id':event_id, 'data':data, 'extra_info':extra_info})     
    
# # generate the hash
# def generateHash(request, txnid, packageAmtPar, packageInfoPar, firstnamePar, emailPar, udf1par, udf2par):
#     try:
#         # get keys and SALT from dashboard once account is created.
#         # hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
#         hash_string = getHashString(request,txnid, packageAmtPar, packageInfoPar, firstnamePar, emailPar, udf1par, udf2par)
#         generated_hash = hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()
#         return generated_hash
#     except Exception as e:
#         # log the error here.
#         logging.getLogger("error_logger").error(traceback.format_exc())
#         return None

# # create hash string using all the fields
# def getHashString(request, txnid, packageAmtPar, packageInfoPar, firstnamePar, emailPar, udf1par, udf2par):
#     hash_string = conf_settings.PAYU_MERCHANT_KEY+"|"+txnid+"|"+str(float(packageAmtPar))+"|"+packageInfoPar+"|"
#     hash_string += firstnamePar+"|"+emailPar+"|"
#     hash_string += str(udf1par)+"|"+str(udf2par)+"|"
#     hash_string += "||||||||"+conf_settings.PAYU_MERCHANT_SALT
#     print('> >>>>>>>>>>',hash_string)
#     return hash_string

# # no csrf token require to go to Success page. 
# # This page displays the success/confirmation message to user indicating the completion of transaction.
# @csrf_exempt
# def package_payment_success(request):
#     ###################NOTE#####################
#     #USE UDF1 for event_id
#     #USE UDF2 for charges_id (FinanceStandardCharges table)
#     ##############ENDS NOTE#####################
   
   
#     payUresp = dict(request.POST)
#     eventId = payUresp['udf1'][0]
#     finance_charges_id = payUresp['udf2'][0] # use for package_brought


#     # query for get user id and email
#     filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=eventId).values('connected_user')
#     connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']

#     filterUserData = Users.objects.get(id = connectedUserId)
#     organizerEmail = filterUserData.user
#     organizerName = filterUserData.firstname
#     # ends here ~ query for get user id and email

    
#     purchaseDate = payUresp['addedon'][0]
#     bookingId = payUresp['payuMoneyId'][0]
#     pricePaid = payUresp['amount'][0]

#     # store required values in package sales
#     filterPackageSales = PackageSales.objects.aggregate(Max('invoice_number'))
#     invoiceNumberMax = filterPackageSales['invoice_number__max']
#     if (invoiceNumberMax == None):
#         PackageSales.objects.create(user_id=connectedUserId, purchase_date=purchaseDate, booking_id=bookingId, price_paid=pricePaid, package_bought=finance_charges_id, invoice_number=0)
#     else:
#         invoiceNumberMax+=1
#         PackageSales.objects.create(user_id=connectedUserId, purchase_date=purchaseDate, booking_id=bookingId, price_paid=pricePaid, package_bought=finance_charges_id, invoice_number=invoiceNumberMax)
#     # ends here ~ store required values in package sales

#     # update leads package on successful payment 
#     StatusPromotionTicketing.objects.filter(event_id=eventId).update(leads_package=finance_charges_id)
#     # ends here ~ update leads package on successful payment 

#     # data for template
#     filterArticles2 = Articles2.objects.get(id = eventId)
#     eventName = filterArticles2.event_name

    
#     filterFinanceStdChg = FinanceStandardCharges.objects.get(charges_id=finance_charges_id)
#     intialPkgPrice = filterFinanceStdChg.fee
#     intialPkgPrice = float(intialPkgPrice)
#     tax_value_num = filterFinanceStdChg.tax_value.split('%')[0]
#     tax_value_num = float(tax_value_num)
#     packageChrgeTaxAmt = (intialPkgPrice/100)*tax_value_num
#     packageTax = str(packageChrgeTaxAmt) + ' ('+filterFinanceStdChg.tax_value + ' ' + filterFinanceStdChg.tax_name+')'
#     # ends here ~ data for template

#     serviceType = filterFinanceStdChg.service_type

#     if (serviceType == 'unlock_rsvp'):
#         servicePackageName = 'Unlock RSVP'
#     elif (serviceType == 'paid_marketing'):
#         servicePackageName = 'Paid Marketing'

#     # send payment success email
#     subject = 'Congratulations! RSVPs for your '+ eventName+' are unlocked.'
#     email_from = conf_settings.EMAIL_HOST_USER
#     recipient_list = [organizerEmail]
#     html_message = render_to_string('static/common/rsvp-paymet-success.html', {
#         'event_name': eventName,
#         'organizer_name': organizerName,
#         'packge_price': intialPkgPrice,
#         'packge_tax': packageTax,
#         'total': pricePaid,
#         'amount_paid': pricePaid,
#         'order_id': bookingId,
#         'packge_name':servicePackageName
#     })
#     msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
#     msg.content_subtype = "html"
#     msg.send(fail_silently=False)
#     # ends here ~ send payment success mail


#     ##################################################
#     ##################################################
#     #############FOR INVOICE DETAILS##################
#     ##################################################
#     ##################################################

#     # get bank details
#     filerBankDetails = BankDetails.objects.get(user_id=connectedUserId)
#     clientGstNumber = filerBankDetails.gst_number
#     # ends here ~ get bank details

#     # generate pdf for invoice
    
#     rsvp_invoice_name = str(uuid.uuid4())+ '_'+str(connectedUserId)+'_'+str(invoiceNumberMax)
#     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     MEDIA_DIR = os.path.join(BASE_DIR, 'media/rsvp_invoice')
#     finalInvoiceName = MEDIA_DIR + "/" + rsvp_invoice_name + '.pdf'
   
#     html_string = render_to_string('static/common/rsvp-invoice.html', {
#         'event_name': eventName,
#         'organizer_name': organizerName,
#         'packge_price': intialPkgPrice,
#         'packge_tax': packageTax,
#         'total': pricePaid,
#         'amount_paid': pricePaid,
#         'order_id': bookingId,
#         'product_name':servicePackageName,
#         'client_gst_number':clientGstNumber,
#         'invoice_number':invoiceNumberMax,
#         'invoice_date':purchaseDate
#     })
#     HTML(string=html_string).write_pdf(finalInvoiceName)
#     invoicePdfFile = open(finalInvoiceName, 'rb')

#     # ends here ~ generate pdf for invoice

#     # send invoice email

#     subject = 'Invoice Details'+ ' '+str(eventName)
#     email_from = conf_settings.EMAIL_HOST_USER
#     recipient_list = [organizerEmail]
#     html_message = 'Hi, Please check attachment file for invoice PDF'
#     msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
#     msg.attach('Unlock RSVP Invoice Details', invoicePdfFile.read(), 'application/pdf')
#     msg.content_subtype = "html"
#     msg.send(fail_silently=False)
#     invoicePdfFile.close()
#     # ends here ~ send invoice email

#     ##################################################
#     ##################################################
#     ########UNLOCK ALL RSVP FOR THIS EVENT############
#     ##################################################
#     ##################################################
#     # unlock all rsvp for this event
#     # Rsvp.objects.filter(event_id=eventId).update(locked=0)
#     # ends here ~ unlock all rsvp for this event

#     return render(request, 'static/common/rsvp-paymet-success.html', {'event_name': eventName,'organizer_name': organizerName,'packge_price': intialPkgPrice,'packge_tax': packageTax,'total': pricePaid,'amount_paid': pricePaid,'order_id': bookingId,'packge_name':servicePackageName})

# no csrf token require to go to Failure page. This page displays the message and reason of failure.
# @csrf_exempt
# def package_payment_fail(request):
#     try:
#         ###################NOTE#####################
#         #USE UDF1 for event_id
#         #USE UDF2 for charges_id (FinanceStandardCharges table)
#         ##############ENDS NOTE#####################
       
       
#         payUresp = dict(request.POST)
#         eventId = payUresp['udf1'][0]

#         # query for get user id and email
#         filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=eventId).values('connected_user')
#         connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']

#         filterUserData = Users.objects.get(id = connectedUserId)
#         organizerEmail = filterUserData.user
#         organizerName = filterUserData.firstname
#         # ends here ~ query for get user id and email

#         # get required data from Articles2 Table
#         filterArticles2 = Articles2.objects.get(id = eventId)
#         eventName = filterArticles2.event_name
#         # ends here ~ get required data from Articles2 Table

#         amountFailed = payUresp['amount'][0]
#         failedTransactionDate = payUresp['addedon'][0]

#         filterFinanceStdChg = FinanceStandardCharges.objects.get(charges_id=finance_charges_id)
#         serviceType = filterFinanceStdChg.service_type

#         if (serviceType == 'unlock_rsvp'):
#             servicePackageName = 'Unlock RSVP'
#         elif (serviceType == 'paid_marketing'):
#             servicePackageName = 'Paid Marketing'


#         try_again_url = 'http://'+request.get_host()+'/live/dashboard/buy-premium-package/'+str(eventId)

#         # send email to organizer on payment failed
#         subject = 'Oops! yur purchase for '+ eventName+' was failed.'
#         email_from = conf_settings.EMAIL_HOST_USER
#         recipient_list = [organizerEmail]
#         html_message = render_to_string('static/common/rsvp-payment-failure.html', {
#             'event_name': eventName,
#             'organizer_name': organizerName,
#             'packge_name':servicePackageName+ ' | ' +amountFailed,
#             'try_again_url':try_again_url
#         })
#         msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
#         msg.content_subtype = "html"
#         msg.send(fail_silently=False)
#         # ends here ~ send email to organizer on payment failed

#         # send email to admin on payment failed for follow up
#         subject = 'Email for Follow up on RSVP Payment Failed ~ '+organizerEmail
#         email_from = conf_settings.EMAIL_HOST_USER
#         recipient_list = ['vishal@ercess.com']
#         html_message = render_to_string('static/common/rsvp-payment-failure-admin.html', {
#             'event_name': eventName,
#             'organizer_name': organizerName,
#             'packge_name':servicePackageName+ ' | ' +amountFailed,
#             'organizer_email':organizerEmail,
#             'transaction_date':failedTransactionDate,
#             'amount_failed':amountFailed,
#             'organizer_id':connectedUserId
#         })
#         msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
#         msg.content_subtype = "html"
#         msg.send(fail_silently=False)
#         # ends here ~ send email to admin on payment failed for follow up


#         return render(request, 'static/common/package-payment-failure.html', {
#             'event_name': eventName,
#             'organizer_name': organizerName,
#             'packge_name':servicePackageName+ ' | ' +amountFailed,
#             'try_again_url':''
#         })
#     except Exception as e:
#         print('error in package_payment_fail function >> ',e)

# def buy_package_manage_events_dashboard(request, event_id):
#     try:
#         filterFinanceStdChrge = FinanceStandardCharges.objects.filter(service_type="paid_marketing").values()
#         paid_marketing_package_list = list(filterFinanceStdChrge)

#         filterFinanceStdChrge = FinanceStandardCharges.objects.filter(service_type="unlock_rsvp").values()
#         unlock_rsvp_list = list(filterFinanceStdChrge)

#         return render(request, 'dashboard/show_package_manage_events_dashboard.html',{'paidPackageList': paid_marketing_package_list,'rsvpPackageList': unlock_rsvp_list, 'event_id':event_id})
#     except Exception as e:
#         print('error in buy_package_manage_events_dashboard function >> ',e)


###############################################################
################# ENDS HERE ~ OLD BUY PACKAGE #################
###############################################################

# ReferrerCashbackInfo, ReferrerCashbackTokens
# function for get cashback info of attendee
@csrf_exempt
def provideCashbackDetails(request, slug):
    try:
        if request.method == 'POST':
            # read request data
            requestData = request.body
            requestDataDecode = requestData.decode('utf8').replace("'", '"')
            requestDataJson = json.loads(requestDataDecode)
            # ends here ~ read request data
            
            # print(requestDataJson)

            mobileNumberVal = requestDataJson['mobile_number']
            paymentPlatformVal = requestDataJson['paymentPlatform']
            emailIdVal = requestDataJson['email_id']
            token = requestDataJson['token']

            try:
                ReferrerTokenData = ReferrerCashbackTokens.objects.get(token_code=token,attendee_email_id=emailIdVal)
                referrerTokenSalesId = ReferrerTokenData.ticket_sales_id
            except Exception as e:
                messageData = {'message': 'This Page link is Broken.', 'responseType': 'success', 'token_type': 'cashback', 'messageType': 'error'}
                context = {}
                context['messageData'] = messageData
                return render(request, 'provide_details_for_cashback.html', context)

            referrerDetailsFilter = ReferrerCashbackInfo.objects.filter(email_id=emailIdVal,ticket_sales_id=referrerTokenSalesId)
            if not referrerDetailsFilter:
                ReferrerCashbackInfo.objects.create(number=mobileNumberVal,payment_platform=paymentPlatformVal,email_id=emailIdVal)
                messageData = {'message': 'Your Details Submitted Successfully', 'responseType': 'success', 'messageType': 'success'}
            else:
                ReferrerCashbackInfo.objects.filter(email_id=emailIdVal,ticket_sales_id=referrerTokenSalesId).update(number=mobileNumberVal,payment_platform=paymentPlatformVal)
                messageData = {'message': 'Your Details Updated Successfully', 'responseType': 'success', 'messageType': 'success'}
            return HttpResponse(json.dumps(messageData))

        else:
            try:
                filterData = ReferrerCashbackTokens.objects.get(
                    token_code=slug)
                referrerId = filterData.attendee_email_id
                messageData = {'message': 'Token is Valid', 'responseType': 'success', 'token_type': 'cashback', 'messageType': 'success', 'email': referrerId}
                context = {}
                context['messageData'] = messageData
                return render(request, 'provide_details_for_cashback.html', context)
            except Exception as e:
                print('error in provideCashbackDetails function >> ',e)
                messageData = {'message': 'This Page link is Broken.', 'responseType': 'success', 'token_type': 'cashback', 'messageType': 'error'}
                context = {}
                context['messageData'] = messageData
                return render(request, 'provide_details_for_cashback.html', context)
    except Exception as e:
        print('error is ', e)
# ends here ~ function for get cashback info of attendee

# function for show different packages on basis of service_type 
@csrf_exempt
def show_rsvp_premium_packages(request, event_id, service_type, purpose_of_payment):
    try:
        # user filter data
        if 'userid' not in request.session.keys():
            return redirect('/live/login')

        userid = request.session.get('userid')
        # ends here ~ user filter data

        if event_id == 0:
            # Get Premium Packages list (only unlock_rsvp) from Finance Standard Charges DB
            filterFinanceStdChrge = FinanceStandardCharges.objects.filter(service_type=service_type).values()
            financeStdChrgeList = list(filterFinanceStdChrge)
            # ends here ~ Get Premium Packages list (only unlock_rsvp) from Finance Standard Charges DB
        else:
            # get country id on basis of event country
            articles2FilterData = Articles2.objects.filter(id=event_id).values()
            articles2FilterList = list(articles2FilterData)
            eventCountryName = articles2FilterList[0]['country']
            eventCountryId = AboutCountries.objects.get(country=eventCountryName).table_id
            eventName = articles2FilterList[0]['event_name']

            # ends here ~ get country id on basis of event country

            # Get Premium Packages list (only unlock_rsvp) from Finance Standard Charges DB
            filterFinanceStdChrge = FinanceStandardCharges.objects.filter(service_type=service_type,country_id=eventCountryId).values()
            financeStdChrgeList = list(filterFinanceStdChrge)
            # ends here ~ Get Premium Packages list (only unlock_rsvp) from Finance Standard Charges DB


        # dynamic title and head text
        if service_type == 'unlock_rsvp':
            title = 'Buy RSVP Package'
            head_text = 'RSVP Package'
        elif service_type == 'paid_marketing':
            title = 'Paid Marketing Package'
            head_text = 'Buy Paid Marketing Package'
        # ends here ~ dynamic title and head text

        return render(request, "dashboard/package-payment-templates/show-rsvp-premium-and-package.html", {'packageList':financeStdChrgeList, 'event_id':event_id,'title':title,'head_text':head_text, 'purpose_of_payment':purpose_of_payment,'event_name':eventName})        
    except Exception as e:
        print('error  in unlock_rsvp function >> ',e)
# ends here ~ function for show different packages on basis of service_type

###############################################################
######################## BUY PACKAGE ##########################
###############################################################

#IMPORTANT NOTE (For PAYUMONEY PAYMENT GATEWAY): All parameter name which start wifh udf's, that is temporary because we don't know about next values.. must need to change in future if include more values (e.g, now, udf2=event_id and udf3=finance_charges_id) & MAX 5 UDF is allowed by PayUMoney

# function for 
def buy_premium_package(request, event_id, charges_id, udf4, udf5, purpose_of_payment):
    # IMPORTANT NOTE
    # productinfo = purpose_of_payment
    # udf1 = userid / current login userid
    # udf2 = event_id
    # udf3 = charges_id
    # udf4 = ? (Will be use in Future, Now Just Pass 0 Int Val for Dummy Purpose)
    # udf5 = custom credit value
    # ENDS HERE ~ IMPORTANT NOTE

    try:
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        userid = request.session.get('userid')
        connectedUserId = userid

        # change here
        total_credit = udf5
        # ends here ~ change here

        # organizer email
        filterUserData = Users.objects.get(id=connectedUserId)
        organizerEmail = filterUserData.user
        # ends here ~ organizer email

        # fetch current package plan on bases on charges_id
        filterFinanceStdChrge = FinanceStandardCharges.objects.filter(charges_id=charges_id).values()
        listFinanceStdChrge = list(filterFinanceStdChrge)
        dictFinanceStdChrge = listFinanceStdChrge[0]
        # ends here ~ fetch current package plan on bases on charges_id


        data = {}
        extra_info = {}
        txnid = getTransactionId()
        # code modify ~ december 26 2019
        if purpose_of_payment == 'sms_credit':
            singleCreditVal = float(dictFinanceStdChrge['fee'])/float(dictFinanceStdChrge['sms'])
        elif purpose_of_payment == 'email_credit':
            singleCreditVal = float(dictFinanceStdChrge['fee'])/float(dictFinanceStdChrge['email'])
        if purpose_of_payment == 'sms_credit' or purpose_of_payment == 'email_credit':
            # calculate price according to credit val
            totalCreditVal = total_credit
            packageCharge = singleCreditVal*totalCreditVal
            # ends here ~ calculate price according to credit val
        else:
            packageCharge = float(dictFinanceStdChrge['fee'])

        # packageCharge = float(dictFinanceStdChrge['fee'])
        # ends here ~ code modify ~ december 26 2019
        tax_value_num = dictFinanceStdChrge['tax_value'].split('%')[0]
        tax_value_num = float(tax_value_num)
        packageChrgeTaxAmt = (packageCharge/100)*tax_value_num
        packageChrgeTaxAmt = round(packageChrgeTaxAmt,1)
        packageChrgeAfterTax = packageCharge + packageChrgeTaxAmt
        packageChrgeAfterTax = round(packageChrgeAfterTax,1)
        extra_info['tax_name'] = dictFinanceStdChrge['tax_name']
        extra_info['tax_value'] = dictFinanceStdChrge['tax_value']
        extra_info['tax_amt'] = packageChrgeTaxAmt
        extra_info['packageChargeBeforeTax'] = packageCharge
        if purpose_of_payment == 'unlock_event_rsvp':
            extra_info['packageName'] = 'Unlock RSVP'

        hash_ = generateHash(request, txnid, packageChrgeAfterTax,purpose_of_payment, filterUserData.firstname, organizerEmail,connectedUserId, event_id, charges_id, udf4, udf5)
        hash_string = getHashString(request, txnid, packageChrgeAfterTax,purpose_of_payment, filterUserData.firstname, organizerEmail,connectedUserId, event_id, charges_id, udf4, udf5)

        # use constants file to store constant values.
        # use test URL for testing
        data["action"] = conf_settings.PAYU_PAYMENT_URL 
        data["amount"] = packageChrgeAfterTax
        data["productinfo"]  = purpose_of_payment
        data["key"] = conf_settings.PAYU_MERCHANT_KEY
        data["txnid"] = txnid
        data["hash"] = hash_
        data["hash_string"] = hash_string
        data["firstname"] = filterUserData.firstname
        data["email"] = organizerEmail
        data["phone"] = filterUserData.mobile
        data["service_provider"] = conf_settings.SERVICE_PROVIDER 
        data["udf1"] = str(connectedUserId) 
        data["udf2"] = str(event_id)
        data["udf3"] = str(charges_id)
        data["udf4"] = str(udf4) # please use relevant variable keyword if you will use in future 
        data["udf5"] = str(udf5) # please use relevant variable keyword if you will use in future
        data["surl"] = request.build_absolute_uri(reverse("dashboard:package-payment-success"))
        data["furl"] = request.build_absolute_uri(reverse("dashboard:package-payment-fail"))
        

        return render(request, "dashboard/package-payment-templates/buy_premium_package.html", {'event_id':event_id, 'data':data, 'extra_info':extra_info})     

    except Exception as e:
        print('Error in buy_premium_package function >> ',e)

# function on payment success
@csrf_exempt
def package_payment_success(request):
    try:
        ###################NOTE#####################
        # productinfo = purpose_of_payment
        # udf1 = userid / current login userid
        # udf2 = event_id
        # udf3 = charges_id
        # udf4 = ? (Will be use in Future, Now Just Pass 0 Int Val for Dummy Purpose)
        # udf5 = ? (Will be use in Future, Now Just Pass 0 Int Val for Dummy Purpose)
        ##############ENDS NOTE#####################

        

        # set udf's variables into local variable (use relevant keyword for ease)
        payUresp = dict(request.POST)
        userid = payUresp['udf1'][0]
        event_id = int(payUresp['udf2'][0])
        charges_id = int(payUresp['udf3'][0])
        total_credit = int(payUresp['udf5'][0])
        purpose_of_payment = payUresp['productinfo'][0]
        # ends here ~ set udf's variables into local variable (use relevant keyword for ease)

        # get email and username of basis of userid
        connectedUserId = userid
        filterUserData = Users.objects.get(id=connectedUserId)
        organizerEmail = filterUserData.user
        organizerName = filterUserData.firstname
        # ends here ~ get email and username of basis of userid

        # get other info from payUmoney response
        purchaseDate = payUresp['addedon'][0]
        bookingId = payUresp['payuMoneyId'][0]
        pricePaid = payUresp['amount'][0]
        # ends here ~ get other info from payUmoney response

        # store required values in package sales table
        filterPackageSales = PackageSales.objects.aggregate(Max('invoice_number'))
        invoiceNumberMax = filterPackageSales['invoice_number__max']
        if (invoiceNumberMax == None):
            PackageSales.objects.create(user_id=connectedUserId, purchase_date=purchaseDate, booking_id=bookingId, price_paid=pricePaid, package_bought=charges_id, invoice_number=0)
        else:
            invoiceNumberMax+=1
            PackageSales.objects.create(user_id=connectedUserId, purchase_date=purchaseDate, booking_id=bookingId, price_paid=pricePaid, package_bought=charges_id, invoice_number=invoiceNumberMax)
        # ends here ~ store required values in package sales table

        # get common data for template
        filterFinanceStdChg = FinanceStandardCharges.objects.get(charges_id=charges_id)
        intialPkgPrice = filterFinanceStdChg.fee
        intialPkgPrice = float(intialPkgPrice)
        tax_value_num = filterFinanceStdChg.tax_value.split('%')[0]
        tax_value_num = float(tax_value_num)
        packageChrgeTaxAmt = (intialPkgPrice/100)*tax_value_num
        packageTax = str(packageChrgeTaxAmt) + ' ('+filterFinanceStdChg.tax_value + ' ' + filterFinanceStdChg.tax_name+')'
        # ends here ~ get common data for template 

        if purpose_of_payment == 'unlock_event_rsvp':
            return unlock_event_rsvp(request,userid, event_id, charges_id, intialPkgPrice, packageTax, pricePaid, bookingId, purpose_of_payment, organizerEmail,organizerName, invoiceNumberMax, purchaseDate)
        elif purpose_of_payment == 'sms_credit' or purpose_of_payment == 'email_credit':
            return add_credit_credit_success(request,userid, event_id, charges_id, intialPkgPrice, packageTax, pricePaid, bookingId, purpose_of_payment, organizerEmail,organizerName, invoiceNumberMax, purchaseDate, total_credit)

    except Exception as e:
        print(' error in package_payment_success function >> ',e)
# ends here ~ function on payment success

# function on payment fail
@csrf_exempt
def package_payment_fail(request):
    try:
        ###################NOTE#####################
        # productinfo = purpose_of_payment
        # udf1 = userid / current login userid
        # udf2 = event_id
        # udf3 = charges_id
        # udf4 = ? (Will be use in Future, Now Just Pass 0 Int Val for Dummy Purpose)
        # udf5 = ? (Will be use in Future, Now Just Pass 0 Int Val for Dummy Purpose)
        ##############ENDS NOTE#####################

        # set udf's variables into local variable (use relevant keyword for ease)
        payUresp = dict(request.POST)
        userid = payUresp['udf1'][0]
        event_id = int(payUresp['udf2'][0])
        charges_id = int(payUresp['udf3'][0])
        purpose_of_payment = payUresp['productinfo'][0]
        # ends here ~ set udf's variables into local variable (use relevant keyword for ease)

        # get email and username of basis of userid
        connectedUserId = userid
        filterUserData = Users.objects.get(id=connectedUserId)
        organizerEmail = filterUserData.user
        organizerName = filterUserData.firstname
        # ends here ~ get email and username of basis of userid

        # get common data from response
        amountFailed = payUresp['amount'][0]
        failedTransactionDate = payUresp['addedon'][0]
        # ends here ~ get common data from response

        if purpose_of_payment == 'unlock_event_rsvp':
            return unlock_event_rsvp_fail(request,userid, event_id, charges_id, purpose_of_payment, organizerEmail,organizerName,amountFailed, failedTransactionDate)
        elif purpose_of_payment == 'sms_credit' or purpose_of_payment == 'email_credit':
            return add_credit_credit_fail(request,userid, event_id, charges_id, intialPkgPrice, packageTax, pricePaid, bookingId, purpose_of_payment, organizerEmail,organizerName, invoiceNumberMax, purchaseDate, purpose_of_payment)



    except Exception as e:
        print(' error in package_payment_fail function >> ',e)
# ends here ~ function on payment fail

# generate a random transaction Id.
def getTransactionId():
    hash_object = hashlib.sha256(str(randint(0,9999)).encode("utf-8"))
    # take approprite length
    txnid = hash_object.hexdigest().lower()[0:32]
    return txnid
# ends here ~ generate a random transaction Id

# generate hash key
def generateHash(request, txnid, packageAmtPar, packageInfoPar, firstnamePar, emailPar, udf1par, udf2par, udf3par, udf4par, udf5par):
    try:
        # get keys and SALT from dashboard once account is created.
        # hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
        hash_string = getHashString(request, txnid, packageAmtPar, packageInfoPar, firstnamePar, emailPar, udf1par, udf2par, udf3par, udf4par, udf5par)
        generated_hash = hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()
        return generated_hash
    except Exception as e:
        error('error in generateHash function >> ',e)
        # logging.getLogger("error_logger").error(traceback.format_exc())
        return None
# ends here ~ generate has 

# generate hash string
def getHashString(request, txnid, packageAmtPar, packageInfoPar, firstnamePar, emailPar, udf1par, udf2par, udf3par, udf4par, udf5par):
    try:
        # create hash string using all the fields
        hash_string = conf_settings.PAYU_MERCHANT_KEY+"|"+txnid+"|"+str(float(packageAmtPar))+"|"+packageInfoPar+"|"
        hash_string += firstnamePar+"|"+emailPar+"|"
        hash_string += str(udf1par)+"|"+str(udf2par)+"|"+str(udf3par)+"|"+str(udf4par)+"|"+str(udf5par)+"|"
        hash_string += '|||||'+conf_settings.PAYU_MERCHANT_SALT
        return hash_string
    except Exception as e:
        print('error in getHashString function >> ',e)
# ends here ~ generate hash string

# function for unlock event rsvp
def unlock_event_rsvp(request,userid, event_id, charges_id, intialPkgPrice, packageTax, pricePaid, bookingId, purpose_of_payment, organizerEmail,organizerName, invoiceNumberMax, purchaseDate):
    try:
        finance_charges_id = charges_id
        eventId = event_id
        connectedUserId = userid

        if purpose_of_payment == 'unlock_event_rsvp':
            package_name = 'Unlock RSVP'

        # update leads package on successful payment 
        StatusPromotionTicketing.objects.filter(event_id=eventId).update(leads_package=finance_charges_id)
        # ends here ~ update leads package on successful payment 

        # data for template
        filterArticles2 = Articles2.objects.get(id = eventId)
        eventName = filterArticles2.event_name
        # ends here ~ data for template

        # send payment success email
        # subject = 'Congratulations! RSVPs for your '+ eventName+' are unlocked.'
        # email_from = conf_settings.EMAIL_HOST_USER
        # recipient_list = [organizerEmail]
        # html_message = render_to_string('static/common/rsvp-paymet-success.html', {
        #     'event_name': eventName,
        #     'organizer_name': organizerName,
        #     'packge_price': intialPkgPrice,
        #     'packge_tax': packageTax,
        #     'total': pricePaid,
        #     'amount_paid': pricePaid,
        #     'order_id': bookingId,
        #     'packge_name':package_name
        # })
        # msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
        # msg.content_subtype = "html"
        # msg.send(fail_silently=False)

        # ends here ~ send payment success mail

        ##################################################
        ##################################################
        #############FOR INVOICE DETAILS##################
        ##################################################
        ##################################################

        # get bank details
        filerBankDetails = BankDetails.objects.get(user_id=connectedUserId)
        clientGstNumber = filerBankDetails.gst_number
        # ends here ~ get bank details

        # generate pdf for invoice

        # html message
        html_message = render_to_string('static/common/rsvp-paymet-success.html', {
            'event_name': eventName,
            'organizer_name': organizerName,
            'packge_price': intialPkgPrice,
            'packge_tax': packageTax,
            'total': pricePaid,
            'amount_paid': pricePaid,
            'order_id': bookingId,
            'packge_name':package_name
        })
        # ends here ~ html message
        
        rsvp_invoice_name = str(uuid.uuid4())+ '_'+str(connectedUserId)+'_'+str(invoiceNumberMax)
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        MEDIA_DIR = os.path.join(BASE_DIR, 'media/invoices')
        finalInvoiceName = MEDIA_DIR + "/" + rsvp_invoice_name + '.pdf'
       
        html_string = render_to_string('static/common/rsvp-invoice.html', {
            'event_name': eventName,
            'organizer_name': organizerName,
            'packge_price': intialPkgPrice,
            'packge_tax': packageTax,
            'total': pricePaid,
            'amount_paid': pricePaid,
            'order_id': bookingId,
            'product_name':package_name,
            'client_gst_number':clientGstNumber,
            'invoice_number':invoiceNumberMax,
            'invoice_date':purchaseDate
        })
        HTML(string=html_string).write_pdf(finalInvoiceName)
        invoicePdfFile = open(finalInvoiceName, 'rb')

        # ends here ~ generate pdf for invoice

        # send invoice email

        subject = 'Congratulations! RSVPs for your '+ eventName+' are unlocked.'
        email_from = conf_settings.EMAIL_HOST_USER
        recipient_list = [organizerEmail]
        # html_message = 'Hi, Please check attachment file for invoice PDF'
        msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
        msg.attach('Unlock RSVP Invoice Details', invoicePdfFile.read(), 'application/pdf')
        msg.content_subtype = "html"
        msg.send(fail_silently=False)
        invoicePdfFile.close()
        # ends here ~ send invoice email

        ##################################################
        ##################################################
        ########UNLOCK ALL RSVP FOR THIS EVENT############
        ##################################################
        ##################################################
        # unlock all rsvp for this event
        Rsvp.objects.filter(event_id=eventId).update(locked=0)
        # ends here ~ unlock all rsvp for this event

        return render(request, 'dashboard/package-payment-templates/payment_success_page_rsvp_premium.html', {'event_name': eventName,'organizer_name': organizerName,'packge_price': intialPkgPrice,'packge_tax': packageTax,'total': pricePaid,'amount_paid': pricePaid,'order_id': bookingId,'packge_name':package_name})

    except Exception as e:
        print(' error in unlock_event_rsvp >> ',e)
# ends here ~ 

def unlock_event_rsvp_fail(request,userid, event_id, charges_id, purpose_of_payment, organizerEmail,organizerName,amountFailed, failedTransactionDate):
    try:
        eventId = event_id
        connectedUserId = userid

        # get required data from Articles2 Table
        filterArticles2 = Articles2.objects.get(id = eventId)
        eventName = filterArticles2.event_name
        # ends here ~ get required data from Articles2 Table

        if purpose_of_payment == 'unlock_event_rsvp':
            package_name = 'Unlock RSVP'
            service_type = 'unlock_rsvp'
            subject_for_email2 = 'Email for Follow up on RSVP Payment Failed - '+organizerEmail

        try_again_url = 'http://'+request.get_host()+'/live/dashboard/show-rsvp-premium-packages/'+str(eventId)+'/'+str(service_type)+'/'+str(purpose_of_payment)

        # send email to organizer on payment failed
        subject = 'Oops! your purchase for '+ eventName+' was failed.'
        email_from = conf_settings.EMAIL_HOST_USER
        recipient_list = [organizerEmail]
        html_message = render_to_string('static/common/rsvp-payment-failure.html', {
            'event_name': eventName,
            'organizer_name': organizerName,
            'packge_name':package_name+' | '+amountFailed,
            'try_again_url':try_again_url
        })
        msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
        msg.content_subtype = "html"
        msg.send(fail_silently=False)
        # ends here ~ send email to organizer on payment failed

        # send email to admin on payment failed for follow up
        subject = subject_for_email2
        email_from = conf_settings.EMAIL_HOST_USER
        recipient_list = ['vishal@ercess.com']
        html_message = render_to_string('static/common/rsvp-payment-failure-admin.html', {
            'event_name': eventName,
            'organizer_name': organizerName,
            'packge_name':package_name +' | '+amountFailed,
            'organizer_email':organizerEmail,
            'transaction_date':failedTransactionDate,
            'amount_failed':amountFailed,
            'organizer_id':connectedUserId,
            'event_id':event_id
        })
        msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
        msg.content_subtype = "html"
        msg.send(fail_silently=False)
        # ends here ~ send email to admin on payment failed for follow up


        return render(request, 'dashboard/package-payment-templates/payment_fail_page_rsvp_premium.html', {
            'event_name': eventName,
            'organizer_name': organizerName,
            'packge_name':package_name,
            'try_again_url':try_again_url,
            'amount_failed':amountFailed
        })
    except Exception as e:
        print('error in unlock_event_rsvp_fail >> ',e)

###############################################################
################## ENDS HERE ~ BUY PACKAGE ####################
###############################################################

#############################################################
############### FUNCTIONALITY FOR SMS MARKETING #############
#############################################################

# function for intial sms marketing form
@csrf_exempt
def sms_marketing_checklist(request, event_id):
    if request.method == 'GET':
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        try:
            articles2FilterData = Articles2.objects.get(id=event_id)
            articlesTicketUrl = articles2FilterData.ticket_url
            eventName = articles2FilterData.event_name
            return render(request, "dashboard/sms-marketing/sms_marketing_checklist.html", {'event_id':event_id, 'event_name':eventName})     
        except Exception as e:
            print('error in GET request | sms_marketing_checklist function >> ',e)

from django.urls import reverse
from django.shortcuts import redirect

@csrf_exempt
def sms_campaign_listing(request, event_id):
    if request.method == 'GET':
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        try:
            #####################################################
            # new modified code ~ december 21 2019

            # Code Block for Fetch Campaign Information
            campaignTemplatesFilter = CampaignTemplates.objects.filter(event_id=event_id,template_type='mobile').values('created_on','scheduled_on','status','template_id')
            cammpaignTemplateLen = len(campaignTemplatesFilter)
            campaignDetailsData = list(campaignTemplatesFilter)


            campaignDetailsList = []
            # totalSmsCount = 0
            for campaign_details in campaignDetailsData:
                campaignDetailsDict = {'created_on':'','scheduled_on':'','status':'','credit_use':''}
                campaignDetailsDict['created_on']=campaign_details['created_on']
                campaignDetailsDict['scheduled_on']=campaign_details['scheduled_on']
                campaignDetailsDict['status']=campaign_details['status']

                ###################################################
                # code block for get total sms count
                campaignTemplateId = campaign_details['template_id']
                smsCount = CampaignStatus.objects.filter(campaign_id=campaignTemplateId).count()
                # totalSmsCount+=smsCount
                campaignDetailsDict['credit_use'] = smsCount
                # ends here ~ code block for get total sms count
                ###################################################

                campaignDetailsList.append(campaignDetailsDict.copy())
            # ends here ~ Code Block for Fetch Campaign Information

            # filter required data from StatusPromotionTicketing table
            statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package','sms_credit')
            statusPromoList = list(statusPromoFilter)
            eventLeadsPackageVal = statusPromoList[0]['leads_package']
            smsCreditVal = statusPromoList[0]['sms_credit']
            # ends here ~ filter required data from StatusPromotionTicketing table



            # set total valid sms limit
            # filterFinanceStdChrge = FinanceStandardCharges.objects.filter(charges_id=eventLeadsPackageVal).values('sms')
            # if(len(filterFinanceStdChrge) == 0):
            #     totalSmsCountUpto = 1000
            # else:
            #     totalSmsVal = filterFinanceStdChrge[0]['sms']
            #     if(totalSmsVal == 0):
            #         totalSmsCountUpto = 1000
            #     else:
            #         totalSmsCountUpto = filterFinanceStdChrge[0]['sms']
            # ends here ~ set total valid sms limit



            # total sms credit left
            # smsCreditLeft = totalSmsCountUpto - totalSmsCount
            smsCreditLeft = smsCreditVal
            # ends here ~ total sms credit left 


            # ends here ~ new modified code ~ december 21 2019
            #####################################################

            # get user id
            user_id = request.session['userid']
            # ends here ~ get user id
            
            # get required data from articles2 table
            articles2FilterData = Articles2.objects.get(id=event_id)
            articlesTicketUrl = articles2FilterData.ticket_url
            eventName = articles2FilterData.event_name
            articleCityName = articles2FilterData.city

            # ends here ~ get required data from articles2 table

            # fetch and set category id and topic id
            filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
            categEvents = list(filterCategEvents)[0]
            catId = categEvents['category_id']
            topicId = categEvents['topic_id']
            # ends here ~ fetch and set category id and topic id

            # get lead count
            # smsSentContactCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(contact='').values_list('contact').distinct().count()
            smsSentContactCount = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(contact='').values_list('contact').distinct().count() 
            # ends here ~ get lead count

            # get data from short url tracker table
            urlShortnerFilter = ShortUrlTracker.objects.filter(event_id=event_id,source='sms_marketing_organizer').values('short_url')
            # ends here ~ get data from UrlMap

            # code for handling short url functionality
            if (len(urlShortnerFilter) == 0):
                shortUrl = url_shortner.create(event_id,articlesTicketUrl,'sms_marketing_organizer')
                print(shortUrl)
            elif(len(urlShortnerFilter) == 1):
                urlShortnerFilter_new = ShortUrlTracker.objects.filter(event_id=event_id, original_url=articlesTicketUrl, source='sms_marketing_organizer').values('short_url')
                if(len(urlShortnerFilter_new) == 1):
                    shortUrl = list(urlShortnerFilter_new)[0]['short_url']
                elif(len(urlShortnerFilter_new) == 0):
                    ShortUrlTracker.objects.filter(event_id=event_id,source='sms_marketing_organizer').update(original_url=articlesTicketUrl)
                    shortUrl = list(urlShortnerFilter)[0]['short_url']
            # ends here ~ code for handling short url functionality

            # make short url
            shortTicketUrl = 'https://' + request.get_host() + '/rcss/'+shortUrl
            # ends here ~ make short url

            # query for check is there any predefined template exists 
            compaignTemplateFilter = CampaignTemplates.objects.filter(user_id=user_id,is_standard=1,template_type='mobile').values('template_msg')
            # ends here ~ query for check is there any predefined template exists

            # set default string for template 
            if(len(compaignTemplateFilter) > 0):
                compaignTemplateList = list(compaignTemplateFilter)
                compaignTemplateList = compaignTemplateList[-1]
                template_msg_data = compaignTemplateList['template_msg']
                is_standard_exists = 'true'
                # remove link from template_msg_data field
                template_msg_data = template_msg_data.split('http')
                template_msg_data = template_msg_data[0]
                # ends here  ~ remove link from template_msg_data field
            else:
                template_msg_data = ''
                is_standard_exists = 'false'
            # ends here ~ set default string for template



            return render(request, "dashboard/sms-marketing/sms_campaign_listing.html", {'event_id':event_id, 'short_ticket_url':shortTicketUrl,'template_msg_data':template_msg_data,'is_standard_exists':is_standard_exists,'event_name':eventName,'campaignDetails':campaignDetailsList, 'total_campaign':cammpaignTemplateLen, 'smsCreditLeft':smsCreditLeft,'smsSentContactCount':smsSentContactCount})     
        except Exception as e:
            print('error in GET request | sms_campaign_listing function >> ',e)


@csrf_exempt
def sms_marketing_initial_details(request, event_id):
    try:
        if request.method == 'GET':
            if 'userid' not in request.session.keys():
                return redirect('/live/login')
            try:
                #####################################################
                # new modified code ~ december 21 2019

                # Code Block for Fetch Campaign Information
                campaignTemplatesFilter = CampaignTemplates.objects.filter(event_id=event_id,template_type='mobile').values('created_on','scheduled_on','status','template_id')
                cammpaignTemplateLen = len(campaignTemplatesFilter)
                campaignDetailsData = list(campaignTemplatesFilter)


                campaignDetailsList = []
                # totalSmsCount = 0
                for campaign_details in campaignDetailsData:
                    campaignDetailsDict = {'created_on':'','scheduled_on':'','status':'','credit_use':''}
                    campaignDetailsDict['created_on']=campaign_details['created_on']
                    campaignDetailsDict['scheduled_on']=campaign_details['scheduled_on']
                    campaignDetailsDict['status']=campaign_details['status']

                    ###################################################
                    # code block for get total sms count
                    campaignTemplateId = campaign_details['template_id']
                    smsCount = CampaignStatus.objects.filter(campaign_id=campaignTemplateId).count()
                    # totalSmsCount+=smsCount
                    campaignDetailsDict['credit_use'] = smsCount
                    # ends here ~ code block for get total sms count
                    ###################################################

                    campaignDetailsList.append(campaignDetailsDict.copy())
                # ends here ~ Code Block for Fetch Campaign Information

                # filter required data from StatusPromotionTicketing table
                statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package','sms_credit')
                statusPromoList = list(statusPromoFilter)
                eventLeadsPackageVal = statusPromoList[0]['leads_package']
                smsCreditVal = statusPromoList[0]['sms_credit']
                # ends here ~ filter required data from StatusPromotionTicketing table



                # set total valid sms limit
                # filterFinanceStdChrge = FinanceStandardCharges.objects.filter(charges_id=eventLeadsPackageVal).values('sms')
                # if(len(filterFinanceStdChrge) == 0):
                #     totalSmsCountUpto = 1000
                # else:
                #     totalSmsVal = filterFinanceStdChrge[0]['sms']
                #     if(totalSmsVal == 0):
                #         totalSmsCountUpto = 1000
                #     else:
                #         totalSmsCountUpto = filterFinanceStdChrge[0]['sms']
                # ends here ~ set total valid sms limit



                # total sms credit left
                # smsCreditLeft = totalSmsCountUpto - totalSmsCount
                smsCreditLeft = smsCreditVal
                # ends here ~ total sms credit left 


                # ends here ~ new modified code ~ december 21 2019
                #####################################################

                # get user id
                user_id = request.session['userid']
                # ends here ~ get user id
                
                # get required data from articles2 table
                articles2FilterData = Articles2.objects.get(id=event_id)
                articlesTicketUrl = articles2FilterData.ticket_url
                eventName = articles2FilterData.event_name
                articleCityName = articles2FilterData.city

                # ends here ~ get required data from articles2 table

                # fetch and set category id and topic id
                filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
                categEvents = list(filterCategEvents)[0]
                catId = categEvents['category_id']
                topicId = categEvents['topic_id']
                # ends here ~ fetch and set category id and topic id

                # get lead count
                # smsSentContactCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(contact='').values_list('contact').distinct().count()
                smsSentContactCount = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(contact='').values_list('contact').distinct().count() 
                # ends here ~ get lead count

                # get data from short url tracker table
                urlShortnerFilter = ShortUrlTracker.objects.filter(event_id=event_id,source='sms_marketing_organizer').values('short_url')
                # ends here ~ get data from UrlMap

                # code for handling short url functionality
                if (len(urlShortnerFilter) == 0):
                    shortUrl = url_shortner.create(event_id,articlesTicketUrl,'sms_marketing_organizer')
                    print(shortUrl)
                elif(len(urlShortnerFilter) == 1):
                    urlShortnerFilter_new = ShortUrlTracker.objects.filter(event_id=event_id, original_url=articlesTicketUrl, source='sms_marketing_organizer').values('short_url')
                    if(len(urlShortnerFilter_new) == 1):
                        shortUrl = list(urlShortnerFilter_new)[0]['short_url']
                    elif(len(urlShortnerFilter_new) == 0):
                        ShortUrlTracker.objects.filter(event_id=event_id,source='sms_marketing_organizer').update(original_url=articlesTicketUrl)
                        shortUrl = list(urlShortnerFilter)[0]['short_url']
                # ends here ~ code for handling short url functionality

                # make short url
                shortTicketUrl = 'https://' + request.get_host() + '/rcss/'+shortUrl
                # ends here ~ make short url

                # query for check is there any predefined template exists 
                compaignTemplateFilter = CampaignTemplates.objects.filter(user_id=user_id,is_standard=1,template_type='mobile').values('template_msg')
                # ends here ~ query for check is there any predefined template exists

                # set default string for template 
                if(len(compaignTemplateFilter) > 0):
                    compaignTemplateList = list(compaignTemplateFilter)
                    compaignTemplateList = compaignTemplateList[-1]
                    template_msg_data = compaignTemplateList['template_msg']
                    is_standard_exists = 'true'
                    # remove link from template_msg_data field
                    template_msg_data = template_msg_data.split('http')
                    template_msg_data = template_msg_data[0]
                    # ends here  ~ remove link from template_msg_data field
                else:
                    template_msg_data = ''
                    is_standard_exists = 'false'
                # ends here ~ set default string for template



                return render(request, "dashboard/sms-marketing/sms_marketing_initial_details.html", {'event_id':event_id, 'short_ticket_url':shortTicketUrl,'template_msg_data':template_msg_data,'is_standard_exists':is_standard_exists,'event_name':eventName,'campaignDetails':campaignDetailsList, 'total_campaign':cammpaignTemplateLen, 'smsCreditLeft':smsCreditLeft,'smsSentContactCount':smsSentContactCount})     
            except Exception as e:
                print('error in GET request | sms_marketing_initial_details function >> ',e)

        if request.method == 'POST':
            try:
                if 'userid' not in request.session.keys():
                    return redirect('/live/login')
                user_id = request.session['userid']
                # read request data
                requestData = request.body
                requestDataDecode = requestData.decode('utf8').replace("'", '"')
                requestDataJson = json.loads(requestDataDecode)
                # ends here ~ read request data

                template_msg = requestDataJson['template_msg']
                template_link = requestDataJson['template_link']
                template_msg += ' '
                template_msg += template_link
                is_standard = requestDataJson['is_standard']

                # insert new data into CampaignTemplates table
                campaignTemplatesObject = CampaignTemplates.objects.create(user_id=user_id,predefined_template_id=0,template_type='mobile',template_msg=template_msg,template_link=template_link,is_standard=is_standard,status='incomplete',created_on=datetime.now(),scheduled_on=datetime.now(),template_subject='',template_image='',event_id=event_id)
                # ends here ~ insert new data into CampaignTemplates table

                # return data to ajax on save data
                filterTempleteId = campaignTemplatesObject.template_id
                nextPageUrl = '/live/dashboard/sms-marketing-advance-details/' + str(event_id)+'/'+str(filterTempleteId)
                previous_page_url='/live/dashboard/sms-marketing-checklist/' + str(event_id)+'?2nd_btn'
                messageData = {'message': 'SMS Template successfully Saved', 'responseType': 'success', 'messageType': 'success', 'url': nextPageUrl, 'event_id':event_id, 'previous_page_url':previous_page_url}
                return HttpResponse(json.dumps(messageData))
                # ends here ~ return data to ajax on save data

            except Exception as e:
                print('error in POST request | sms_marketing_initial_details function >> ',e)
    except Exception as e:
        print('error in sms_marketing_initial_details function >> ',e)
# ends here ~ function for intial sms marketing form

# common function for add sms campaign data in leads table addLeads
def addSmsCampaignDataInLeads(user_id, event_id, submitType, contactCsvFile, isAddLeads):
    try:
        # get package id on basis of event id
        statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package','sms_credit')
        statusPromoList = list(statusPromoFilter)
        smsCreditLeft = statusPromoList[0]['sms_credit']
        # ends here ~ get package id on basis of event id

        # fetch and set category id and topic id
        filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
        categEvents = list(filterCategEvents)[0]
        catId = categEvents['category_id']
        topicId = categEvents['topic_id']
        # ends here ~ fetch and set category id and topic id

        # fetch city name from articles 2 table
        filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
        articleCityName = list(filterArtiData)[0]['city']
        articleEventName = list(filterArtiData)[0]['event_name']
        # ends here ~ fetch city name from articles 2 table

        # read file and other data
        decodedCsvFile = contactCsvFile
        # ends here ~ read file and other data


        duplicateRecords = 0
        successfulAddedRecords = 0
        failedRecords = 0
        currentRow = 1
        failedRowList = []
        loop_count = 0
        totalValidContacts = 0

        ###################################################
        for number_list in (r[0:3] for r in csv.reader(decodedCsvFile)):
            numberRegex=re.compile('^[0-9]{10}$')
            for number in number_list:
                numberValid = numberRegex.match(number)
                if(numberValid != None):
                    totalValidContacts+=1
                    # leadsFilterData = Leads.objects.filter(contact=number,city=articleCityName,category=catId)                    
                    leadsFilterData = Leads.objects.filter(user_id=user_id,contact=number,city=articleCityName,category=catId)
                    if not leadsFilterData:
                        # save rsvp personal data to additional leads table
                        # if isAddLeads == True:
                        Leads.objects.create(name='',email='',contact=number,category=catId,sub_category=topicId,city=articleCityName,user_id=user_id)
                        loop_count+=1
                        successfulAddedRecords+=1
                        # ends here ~ save rsvp personal data to additional leads table
                    else:
                        duplicateRecords+=1
                else:
                    failedRecords+=1

        #####################################################

        # smsSentContactCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(contact='').values_list('contact').distinct().count()
        smsSentContactCount = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(contact='').values_list('contact').distinct().count()

        if isAddLeads == False:
            # # get total lead count
            # totalLeadCount = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId,sub_category=topicId).count()
            # totalLeadCount+=successfulAddedRecords
            # # ends here ~ get total lead count

            # # get total sms count from db
            # campaignTemplatesFilter = CampaignTemplates.objects.filter(event_id=event_id,template_type='mobile').values('template_id')
            # cammpaignTemplateLen = len(campaignTemplatesFilter)
            # campaignDetailsData = list(campaignTemplatesFilter)
            # totalSmsCount = 0
            # for campaign_details in campaignDetailsData:
            #     campaignTemplateId = campaign_details['template_id']
            #     smsCount = CampaignStatus.objects.filter(campaign_id=campaignTemplateId).count()
            #     totalSmsCount+=smsCount
            # # ends here ~ get total sms count from db

            # # total new contact
            # newContactCount = totalLeadCount - totalSmsCount
            # totalNewCreditRequire = newContactCount - smsCreditLeft 
            # # ends here ~ total new contact
            newContactCount = successfulAddedRecords
            totalNewCreditRequire = newContactCount - smsCreditLeft

            if(smsCreditLeft < smsSentContactCount):
                # updated data dict
                csvContactUploadResult = {'duplicateRecords':duplicateRecords,'totalValidContacts':totalValidContacts,'failedRecords':failedRecords,'successfulAddedRecords':successfulAddedRecords,'smsCreditLeft':smsCreditLeft,'newContactCount':newContactCount,'newCreditRequire':totalNewCreditRequire,'smsSentContactCount':smsSentContactCount}
                # ends here ~ updated data dict

                textMessage = 'You only have '+str(smsCreditLeft)+' credits and total contacts are '+str(smsSentContactCount)+', would you like to purchase more credits or restrict to the available credits'
                messageData = {'message': textMessage, 'responseType': 'success', 'messageType': 'error', 'data':csvContactUploadResult}
                return HttpResponse(json.dumps(messageData))
            else:
                return True
        else:

            #@author Shubham ~ modify code ~ december 19 2019
            csvContactUploadResult = {'duplicateRecords':duplicateRecords,'totalValidContacts':totalValidContacts,'failedRecords':failedRecords,'successfulAddedRecords':successfulAddedRecords,'smsSentContactCount':smsSentContactCount}  
            messageData = {'message': '', 'responseType': 'success', 'messageType': 'success', 'data':csvContactUploadResult}
            return HttpResponse(json.dumps(messageData))
            
    except Exception as e:
        print('error in addSmsCampaignDataInLeads function >> ',e)
        textMessage = 'We have a hard time to read your file. Please download the samlpe file given above and copy all the contact and upload again.'
        messageData = {'message': textMessage, 'responseType': 'success', 'messageType': 'error', 'data':[]}
        return HttpResponse(json.dumps(messageData))
# ends here ~ common function for add sms campaign data in leads table

# function for advance sms marketing form
@csrf_exempt
def sms_marketing_advance_details(request, event_id,template_id):
    try:
        if request.method == 'GET':
            if 'userid' not in request.session.keys():
                return redirect('/live/login')
            try:
                statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package','sms_credit')
                statusPromoList = list(statusPromoFilter)
                smsCreditVal = statusPromoList[0]['sms_credit']



                # get user id
                user_id = request.session['userid']
                # ends here ~ get user id

                # get required data from articles2 table
                articles2FilterData = Articles2.objects.get(id=event_id)
                eventEndDate = articles2FilterData.edate
                eventName = articles2FilterData.event_name
                # ends here ~ get required data from articles2 table

                # fetch and set category id and topic id
                filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
                categEvents = list(filterCategEvents)[0]
                catId = categEvents['category_id']
                topicId = categEvents['topic_id']
                # ends here ~ fetch and set category id and topic id

                # fetch city name from articles 2 table
                filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
                articleCityName = list(filterArtiData)[0]['city']
                articleEventName = list(filterArtiData)[0]['event_name']
                # ends here ~ fetch city name from articles 2 table

                # leads count
                # leadCount = CampaignStatus.objects.filter(campaign_id=template_id).count()
                # leadCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(contact='').count()
                # leadCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(contact='').values_list('contact').distinct().count()
                leadCount = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(contact='').values_list('contact').distinct().count()

                # ends here ~ leads count

                return render(request, "dashboard/sms-marketing/sms_marketing_advance_details.html", {'event_id':event_id,'template_id':template_id,'event_end_date':eventEndDate, 'contactCount':leadCount, 'event_name':eventName, 'smsCreditVal':smsCreditVal })     
            except Exception as e:
                print('error in GET request | sms_marketing_advance_details function >> ',e)

        if request.method == 'POST':
            try:
                if 'userid' not in request.session.keys():
                    return redirect('/live/login')
                user_id = request.session['userid']
                
                # read request data
                event_id = request.POST['event_id']
                submitType = request.POST['submitType']
                contactCsvFile = request.FILES['file']
                decodedCsvFile = contactCsvFile.read().decode('utf-8').splitlines()
                # ends here ~ read request data

                if submitType == 'normalSubmit':
                    checkUserSmsCredit = addSmsCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, False)
                    if checkUserSmsCredit == True:
                        return addSmsCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, True)
                    else:
                        return checkUserSmsCredit
                else:
                    return addSmsCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, True)

                # ends here ~ @author Shubham ~ modify code ~ december 19 2019
                # #####################################################

                # ends here ~ store values into db upto totalSmsVal contacts (if leads_package!=0)

            except Exception as e:
                print('error in POST request | sms_marketing_advance_details function >> ',e)
    except Exception as e:
        print('error in sms_marketing_advance_details function >> ',e)

@csrf_exempt
def sms_marketing_success_page(request, event_id):
    if request.method == 'GET':
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        try:
            statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package','sms_credit')
            statusPromoList = list(statusPromoFilter)
            smsCreditVal = statusPromoList[0]['sms_credit']



            # get user id
            user_id = request.session['userid']
            # ends here ~ get user id

            # get required data from articles2 table
            articles2FilterData = Articles2.objects.get(id=event_id)
            eventEndDate = articles2FilterData.edate
            eventName = articles2FilterData.event_name
            # ends here ~ get required data from articles2 table

            # fetch and set category id and topic id
            filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
            categEvents = list(filterCategEvents)[0]
            catId = categEvents['category_id']
            topicId = categEvents['topic_id']
            # ends here ~ fetch and set category id and topic id

            # fetch city name from articles 2 table
            filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
            articleCityName = list(filterArtiData)[0]['city']
            articleEventName = list(filterArtiData)[0]['event_name']
            # ends here ~ fetch city name from articles 2 table

            # leads count
            # leadCount = CampaignStatus.objects.filter(campaign_id=template_id).count()
            # leadCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(contact='').count()
            # leadCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(contact='').values_list('contact').distinct().count()
            leadCount = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(contact='').values_list('contact').distinct().count()

            # ends here ~ leads count

            return render(request, "dashboard/sms-marketing/sms_marketing_success_page.html", {'event_id':event_id,'event_end_date':eventEndDate, 'contactCount':leadCount, 'event_name':eventName, 'smsCreditVal':smsCreditVal })     
        except Exception as e:
                print('error in GET request | sms_marketing_success_page function >> ',e)

@csrf_exempt
def sms_marketing_advance_details_scheduling(request, event_id,template_id):
    try:
        if request.method == 'GET':
            if 'userid' not in request.session.keys():
                return redirect('/live/login')
            try:
                statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package','sms_credit')
                statusPromoList = list(statusPromoFilter)
                smsCreditVal = statusPromoList[0]['sms_credit']



                # get user id
                user_id = request.session['userid']
                # ends here ~ get user id

                # get required data from articles2 table
                articles2FilterData = Articles2.objects.get(id=event_id)
                eventEndDate = articles2FilterData.edate
                eventName = articles2FilterData.event_name
                # ends here ~ get required data from articles2 table

                # fetch and set category id and topic id
                filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
                categEvents = list(filterCategEvents)[0]
                catId = categEvents['category_id']
                topicId = categEvents['topic_id']
                # ends here ~ fetch and set category id and topic id

                # fetch city name from articles 2 table
                filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
                articleCityName = list(filterArtiData)[0]['city']
                articleEventName = list(filterArtiData)[0]['event_name']
                # ends here ~ fetch city name from articles 2 table

                # leads count
                # leadCount = CampaignStatus.objects.filter(campaign_id=template_id).count()
                # leadCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(contact='').count()
                # leadCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(contact='').values_list('contact').distinct().count()
                leadCount = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(contact='').values_list('contact').distinct().count()

                # ends here ~ leads count

                return render(request, "dashboard/sms-marketing/sms_marketing_advance_details_scheduling.html", {'event_id':event_id,'template_id':template_id,'event_end_date':eventEndDate, 'contactCount':leadCount, 'event_name':eventName, 'smsCreditVal':smsCreditVal })     
            except Exception as e:
                print('error in GET request | sms_marketing_advance_details_scheduling function >> ',e)

        if request.method == 'POST':
            try:
                if 'userid' not in request.session.keys():
                    return redirect('/live/login')
                user_id = request.session['userid']
                
                # read request data
                event_id = request.POST['event_id']
                submitType = request.POST['submitType']
                contactCsvFile = request.FILES['file']
                decodedCsvFile = contactCsvFile.read().decode('utf-8').splitlines()
                # ends here ~ read request data

                if submitType == 'normalSubmit':
                    checkUserSmsCredit = addSmsCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, False)
                    if checkUserSmsCredit == True:
                        return addSmsCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, True)
                    else:
                        return checkUserSmsCredit
                else:
                    return addSmsCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, True)

                # ends here ~ @author Shubham ~ modify code ~ december 19 2019
                # #####################################################

                # ends here ~ store values into db upto totalSmsVal contacts (if leads_package!=0)

            except Exception as e:
                print('error in POST request | sms_marketing_advance_details function >> ',e)
    except Exception as e:
        print('error in sms_marketing_advance_details function >> ',e)
# ends here ~ function for advance sms marketing form

# # function for advance sms marketing form
# @csrf_exempt
# def sms_marketing_advance_details(request, event_id,template_id):
#     try:
#         if request.method == 'GET':
#             if 'userid' not in request.session.keys():
#                 return redirect('/live/login')
#             try:
#                 # get user id
#                 user_id = request.session['userid']
#                 # ends here ~ get user id

#                 # get required data from articles2 table
#                 articles2FilterData = Articles2.objects.get(id=event_id)
#                 eventEndDate = articles2FilterData.edate
#                 eventName = articles2FilterData.event_name
#                 # ends here ~ get required data from articles2 table

#                 # fetch and set category id and topic id
#                 filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
#                 categEvents = list(filterCategEvents)[0]
#                 catId = categEvents['category_id']
#                 topicId = categEvents['topic_id']
#                 # ends here ~ fetch and set category id and topic id

#                 # fetch city name from articles 2 table
#                 filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
#                 articleCityName = list(filterArtiData)[0]['city']
#                 articleEventName = list(filterArtiData)[0]['event_name']
#                 # ends here ~ fetch city name from articles 2 table

#                 # leads count
#                 # leadCount = CampaignStatus.objects.filter(campaign_id=template_id).count()
#                 leadCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(contact='').count()
#                 # ends here ~ leads count

#                 return render(request, "dashboard/sms-marketing/sms_marketing_advance_details.html", {'event_id':event_id,'template_id':template_id,'event_end_date':eventEndDate, 'contactCount':leadCount, 'event_name':eventName})     
#             except Exception as e:
#                 print('error in GET request | sms_marketing_advance_details function >> ',e)

#         if request.method == 'POST':
#             try:
#                 if 'userid' not in request.session.keys():
#                     return redirect('/live/login')
#                 user_id = request.session['userid']
#                 # read request data

#                 event_id = request.POST['event_id']
#                 submitType = request.POST['submitType']

#                 # get package id on basis of event id
#                 statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package','sms_credit')
#                 statusPromoList = list(statusPromoFilter)
#                 eventLeadsPackageVal = statusPromoList[0]['leads_package']
#                 smsCreditLeft = statusPromoList[0]['sms_credit']
#                 # ends here ~ get package id on basis of event id

#                 # fetch and set category id and topic id
#                 filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
#                 categEvents = list(filterCategEvents)[0]
#                 catId = categEvents['category_id']
#                 topicId = categEvents['topic_id']
#                 # ends here ~ fetch and set category id and topic id

#                 # fetch city name from articles 2 table
#                 filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
#                 articleCityName = list(filterArtiData)[0]['city']
#                 articleEventName = list(filterArtiData)[0]['event_name']
#                 # ends here ~ fetch city name from articles 2 table

#                 # read file and other data
#                 contactCsvFile = request.FILES['file']
#                 decodedCsvFile = contactCsvFile.read().decode('utf-8').splitlines()
#                 # ends here ~ read file and other data

#                 # set total valid sms limit
#                 # filterFinanceStdChrge = FinanceStandardCharges.objects.filter(charges_id=eventLeadsPackageVal).values('sms')
#                 # if(len(filterFinanceStdChrge) == 0):
#                 #     totalSmsCountUpto = 1001
#                 # else:
#                 #     totalSmsVal = filterFinanceStdChrge[0]['sms']
#                 #     if(totalSmsVal == 0):
#                 #         totalSmsCountUpto = 1001
#                 #     else:
#                 #         totalSmsCountUpto = filterFinanceStdChrge[0]['sms'] + 1
#                 # ends here ~ set total valid sms limit

#                 duplicateRecords = 0
#                 successfulAddedRecords = 0
#                 failedRecords = 0
#                 currentRow = 1
#                 failedRowList = []
#                 loop_count = 0
#                 totalValidContacts = 0

#                 ###################################################
#                 # new code ~ december 24 & december 25
#                 if submitType == 'normalSubmit':

#                     for number_list in (r[0:3] for r in csv.reader(decodedCsvFile)):
#                     numberRegex=re.compile('^[0-9]{10}$')
#                     for number in number_list:
#                         numberValid = numberRegex.match(number)
#                         if(numberValid != None):
#                             totalValidContacts+=1
#                             leadsFilterData = Leads.objects.filter(contact=number,city=articleCityName,category=catId)
#                             if not leadsFilterData:
#                                 # save rsvp personal data to additional leads table
#                                 loop_count+=1
#                                 successfulAddedRecords+=1
#                                 # ends here ~ save rsvp personal data to additional leads table
#                             else:
#                                 duplicateRecords+=1
#                         else:
#                             failedRecords+=1

#                     # get total lead count
#                     totalLeadCount = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId,sub_category=topicId).count()
#                     totalLeadCount+=successfulAddedRecords
#                     # ends here ~ get total lead count

#                     # get total sms count from db
#                     campaignTemplatesFilter = CampaignTemplates.objects.filter(event_id=event_id,template_type='mobile').values('template_id')
#                     cammpaignTemplateLen = len(campaignTemplatesFilter)
#                     campaignDetailsData = list(campaignTemplatesFilter)
#                     totalSmsCount = 0
#                     for campaign_details in campaignDetailsData:
#                         campaignTemplateId = campaign_details['template_id']
#                         smsCount = CampaignStatus.objects.filter(campaign_id=campaignTemplateId).count()
#                         totalSmsCount+=smsCount
#                     # ends here ~ get total sms count from db

#                     # total new contact
#                     newContactCount = totalLeadCount - totalSmsCount
#                     totalNewCreditRequire = newContactCount - smsCreditLeft 
#                     # ends here ~ total new contact

#                     if(smsCreditLeft < newContactCount):
#                         # updated data dict
#                         csvContactUploadResult = {'duplicateRecords':0,'totalValidContacts':0,'failedRecords':0,'successfulAddedRecords':0,'smsCreditLeft':smsCreditLeft,'newContactCount':newContactCount,'newCreditRequire':totalNewCreditRequire}
#                         # ends here ~ updated data dict
#                         textMessage = 'You only have '+str(smsCreditLeft)+' credits and total contacts are '+str(newContactCount)+', would you like to purchase more credits or restrict to the available credits'
#                         messageData = {'message': textMessage, 'responseType': 'success', 'messageType': 'error', 'data':csvContactUploadResult}
#                         return HttpResponse(json.dumps(messageData))
#                 # ends here ~  new code ~ december 24 & december 25
#                 ###################################################

#                 # reset val
#                 duplicateRecords = 0
#                 successfulAddedRecords = 0
#                 failedRecords = 0
#                 currentRow = 1
#                 failedRowList = []
#                 loop_count = 0
#                 totalValidContacts = 0
#                 # ends here ~ reset val

#                 for number_list in (r[0:3] for r in csv.reader(decodedCsvFile)):
#                     numberRegex=re.compile('^[0-9]{10}$')
#                     for number in number_list:
#                         numberValid = numberRegex.match(number)
#                         if(numberValid != None):
#                             totalValidContacts+=1
#                             leadsFilterData = Leads.objects.filter(contact=number,city=articleCityName,category=catId)
#                             if not leadsFilterData:
#                                 # save rsvp personal data to additional leads table
#                                 Leads.objects.create(name='',email='',contact=number,category=catId,sub_category=topicId,city=articleCityName,user_id=user_id)
#                                 loop_count+=1
#                                 successfulAddedRecords+=1
#                                 # ends here ~ save rsvp personal data to additional leads table
#                             else:
#                                 duplicateRecords+=1
#                         else:
#                             failedRecords+=1

#                 # #####################################################
#                 # @author Shubham ~ modify code ~ december 19 2019
#                 csvContactUploadResult = {'duplicateRecords':duplicateRecords,'totalValidContacts':totalValidContacts,'failedRecords':failedRecords,'successfulAddedRecords':successfulAddedRecords}  
#                 messageData = {'message': '', 'responseType': 'success', 'messageType': 'success', 'data':csvContactUploadResult}
#                 return HttpResponse(json.dumps(messageData))
#                 # return data to ajax on save data
#                 # if loop_count == 0 and duplicateRecords == 0:
#                 #     messageData = {'message': 'No contacts synced. Make sure to include only numbers in CSV file.', 'responseType': 'success', 'messageType': 'error'}
#                 # elif loop_count == 0 and duplicateRecords > 0:
#                 #     messageData = {'message': 'No contacts synced. '+str(duplicateRecords)+' duplicate records found', 'responseType': 'success', 'messageType': 'error'}
#                 # elif loop_count > 0:
#                 #     messageData = {'message': 'All valid contacts synced', 'responseType': 'success', 'messageType': 'success'}
#                 # return HttpResponse(json.dumps(messageData))
#                 # ends here ~ return data to ajax on save data
#                 # ends here ~ @author Shubham ~ modify code ~ december 19 2019
#                 # #####################################################

#                 # ends here ~ store values into db upto totalSmsVal contacts (if leads_package!=0)

#             except Exception as e:
#                 print('error in POST request | sms_marketing_advance_details function >> ',e)
#     except Exception as e:
#         print('error in sms_marketing_advance_details function >> ',e)
# # ends here ~ function for advance sms marketing form

# save scheduled values sms marketing
@csrf_exempt
def sms_marketing_schedule(request):
    try:
        if request.method == 'GET':
            if 'userid' not in request.session.keys():
                return redirect('/live/login')
        if request.method == 'POST':
            try:
                if 'userid' not in request.session.keys():
                    return redirect('/live/login')
                user_id = request.session['userid']
                # read request data
                requestData = request.body
                requestDataDecode = requestData.decode('utf8').replace("'", '"')
                requestDataJson = json.loads(requestDataDecode)
                # ends here ~ read request data

                # set value into variables
                event_id = requestDataJson['event_id']
                template_id = requestDataJson['template_id']
                scheduled_on_date = requestDataJson['scheduled_on_date']
                scheduled_on_time = requestDataJson['scheduled_on_time']
                # ends here ~ set value into variables

                # update schedule datetime according to template id
                scheduledDateTime = datetime.strptime(scheduled_on_date +' '+scheduled_on_time, '%d/%m/%Y %I:%M %p')
                CampaignTemplates.objects.filter(template_id=template_id).update(scheduled_on=scheduledDateTime)
                # ends here ~ update schedule datetime according to template id

                # get package id on basis of event id
                statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package')
                statusPromoList = list(statusPromoFilter)
                eventLeadsPackageVal = statusPromoList[0]['leads_package']
                # ends here ~ get package id on basis of event id

                # set total valid sms limit
                # filterFinanceStdChrge = FinanceStandardCharges.objects.filter(charges_id=eventLeadsPackageVal).values('sms')
                # if(len(filterFinanceStdChrge) == 0):
                #     totalSmsCountUpto = 1001
                # else:
                #     totalSmsVal = filterFinanceStdChrge[0]['sms']
                #     if(totalSmsVal == 0):
                #         totalSmsCountUpto = 1001
                #     else:
                #         totalSmsCountUpto = filterFinanceStdChrge[0]['sms'] + 1
                # ends here ~ set total valid sms limit

                statusPromoFilter = StatusPromotionTicketing.objects.get(event_id=event_id)
                newTotalCredits = statusPromoFilter.sms_credit
                totalSmsCountUpto = newTotalCredits
                # fetch and set category id and topic id
                filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
                categEvents = list(filterCategEvents)[0]
                catId = categEvents['category_id']
                topicId = categEvents['topic_id']
                # ends here ~ fetch and set category id and topic id

                # fetch city name from articles 2 table
                filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
                articleCityName = list(filterArtiData)[0]['city']
                articleEventName = list(filterArtiData)[0]['event_name']
                # ends here ~ fetch city name from articles 2 table

                # copy data from leads table to campaign status table
                # orignalTotalSmsCountUpto = totalSmsCountUpto-1
                orignalTotalSmsCountUpto = totalSmsCountUpto
                # leadsFilterData = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId,sub_category=topicId).order_by('-id')[:orignalTotalSmsCountUpto].values()
                leadsFilterData = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(contact='').values_list('contact').distinct().order_by('-id')[:orignalTotalSmsCountUpto].values()
                leadsFilterList = list(leadsFilterData)
                loop_count=0

                # loop on Leads table last "orignalTotalSmsCountUpto" rows filter data 
                for leadsData in leadsFilterList:
                    contactNumber = leadsData['contact']
                    if contactNumber != '' and contactNumber != None:
                        # if contact number field is not empty
                        campaignStatusFilter = CampaignStatus.objects.filter(contact=contactNumber,campaign_id=template_id).values()
                        if(len(campaignStatusFilter) == 0):
                            # if contact is not already stored in CampaignStatus table with same campaign_id 
                            if loop_count == totalSmsCountUpto:
                                    break
                            CampaignStatus.objects.create(campaign_id=template_id, contact=contactNumber,contact_type='mobile',created_on=datetime.now(),updated_on=datetime.now(),status='scheduled')
                            loop_count+=1
                # ends here ~ loop on Leads table last "orignalTotalSmsCountUpto" rows filter data

                # ends here ~ copy data from leads table to campaign status table

                # update StatusPromotionTicketing Table
                leftSmsCredit = newTotalCredits - loop_count
                if leftSmsCredit < 0:
                    leftSmsCredit = 0
                StatusPromotionTicketing.objects.filter(event_id=event_id).update(sms_credit=leftSmsCredit)
                # ends here ~ update StatusPromotionTicketing Table

                # required data for ajax response
                schedule_data = {}
                campaignTemplatesFilter = CampaignTemplates.objects.get(template_id=template_id)
                templateMsg = campaignTemplatesFilter.template_msg
                # remove link from templateMsg field
                templateMsg = templateMsg.split('http')
                templateMsg = templateMsg[0]
                # ends here  ~ remove link from templateMsg field
                templateLink = campaignTemplatesFilter.template_link
                leadContactCount = CampaignStatus.objects.filter(campaign_id=template_id).exclude(contact='').count()
                # leadContactCount = Leads.objects.filter(user_id=user_id).count()

                schedule_data['date_time'] = str(scheduled_on_date +' '+scheduled_on_time)
                schedule_data['templateMsg'] = templateMsg
                schedule_data['templateLink'] = templateLink
                schedule_data['totalContactCount'] = leadContactCount
                # ends here ~ required data for ajax response 

                # get user email
                filterUserData = Users.objects.get(id = user_id)
                organizerEmail = filterUserData.user
                # ends here ~ get user email

                # send email on completion of sms marketing campaign
                subject = 'Congratulations! New SMS Marketing Campaign Created Successfully'
                email_from = conf_settings.EMAIL_HOST_USER
                recipient_list = [organizerEmail]
                html_message = render_to_string('static/common/sms_marketing_success.html',
                    {
                    'campaign_scheduled_date_time': schedule_data['date_time'],
                    'campaign_total_contacts': schedule_data['totalContactCount'],
                    'campaign_message': schedule_data['templateMsg'],
                    'campaign_short_link': schedule_data['templateLink'],
                    'event_name': articleEventName
                })

                try:
                    msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'track@ercess.com'})
                    msg.content_subtype = "html"
                    msg.send(fail_silently=False)
                except Exception as e:
                    pass

                # ends here ~ send email on completion of sms marketing campaign

                # return data to ajax after save data
                messageData = {'message': 'All Contacts Uploaded', 'responseType': 'success', 'messageType': 'success','data':schedule_data}
                return HttpResponse(json.dumps(messageData))
                # ends here ~ return data to ajax after save data

            except Exception as e:
                print('error in POST request | sms_marketing_schedule_details function >> ',e)
    except Exception as e:
        print('error in sms_marketing_schedule_details function >> ',e)
# ends here ~ save scheduled values sms marketing

#############################################################
####### ENDS HERE ~  FUNCTIONALITY FOR SMS MARKETING ########
#############################################################

#############################################################
############## FUNCTIONALITY FOR EMAIL MARKETING ############
#############################################################

# function for select template for email marketing

@csrf_exempt
def email_marketing_checklist(request, event_id):
    if request.method == 'GET':
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        try:
            articles2FilterData = Articles2.objects.get(id=event_id)
            articlesTicketUrl = articles2FilterData.ticket_url
            eventName = articles2FilterData.event_name
            return render(request, "dashboard/email-marketing/email_marketing_checklist.html", {'event_id':event_id, 'event_name':eventName})     
        except Exception as e:
            print('error in GET request | email_marketing_checklist function >> ',e)

def email_campaign_listing(request, event_id):
    try:
        # code for get request
        if request.method == 'GET':
            try:
                if 'userid' not in request.session.keys():
                    return redirect('/live/login')

                 #####################################################
                # new modified code ~ december 21 2019

                # Code Block for Fetch Campaign Information
                campaignTemplatesFilter = CampaignTemplates.objects.filter(event_id=event_id,template_type='email').values('created_on','scheduled_on','status','template_id')
                cammpaignTemplateLen = len(campaignTemplatesFilter)
                campaignDetailsData = list(campaignTemplatesFilter)

                campaignDetailsList = []
                # totalEmailCount = 0
                for campaign_details in campaignDetailsData:
                    campaignDetailsDict = {'created_on':'','scheduled_on':'','status':'','credit_use':''}
                    campaignDetailsDict['created_on']=campaign_details['created_on']
                    campaignDetailsDict['scheduled_on']=campaign_details['scheduled_on']
                    campaignDetailsDict['status']=campaign_details['status']

                    ###################################################
                    # code block for get total email count
                    campaignTemplateId = campaign_details['template_id']
                    emailCount = CampaignStatus.objects.filter(campaign_id=campaignTemplateId).count()
                    # totalEmailCount+=emailCount
                    campaignDetailsDict['credit_use'] = emailCount
                    # ends here ~ code block for get total email count
                    ###################################################

                    campaignDetailsList.append(campaignDetailsDict.copy())
                # ends here ~ Code Block for Fetch Campaign Information

                # filter required data from StatusPromotionTicketing table
                statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package','email_credit')
                statusPromoList = list(statusPromoFilter)
                eventLeadsPackageVal = statusPromoList[0]['leads_package']
                emailCreditVal = statusPromoList[0]['email_credit']
                # ends here ~ filter required data from StatusPromotionTicketing table

                # set total valid email limit
                # filterFinanceStdChrge = FinanceStandardCharges.objects.filter(charges_id=eventLeadsPackageVal).values('email')
                # if(len(filterFinanceStdChrge) == 0):
                #     totalEmailCountUpto = 1000
                # else:
                #     totalEmailVal = filterFinanceStdChrge[0]['email']
                #     if(totalEmailVal == 0):
                #         totalEmailCountUpto = 1000
                #     else:
                #         totalEmailCountUpto = filterFinanceStdChrge[0]['email']
                # ends here ~ set total valid email limit

                # total email credit left
                # emailCreditLeft = totalEmailCountUpto - totalEmailCount
                emailCreditLeft = emailCreditVal
                # ends here ~ total email credit left 


                # ends here ~ new modified code ~ december 21 2019
                #####################################################

                # read files name from folder
                emailMarketingPreviewTmpt = os.path.join(BASE_DIR, 'templates/static/common/email_templates')
                emailMarketingPreviewTmptFiles = [f for f in listdir(emailMarketingPreviewTmpt) if isfile(join(emailMarketingPreviewTmpt, f))]
                # ends here ~ read files name from folder
                
                # blank dict and list for preview email for showing in ui 
                emailMarketingPreviewTmpDict = {'filename':'','preview_html_template':'', 'filename_without_ext':''}
                emailMarketingPreviewTmptList = []
                # ends here ~ blank dict and list for preview email for showing in ui

                # for loop on email marketing preview template file names (emailMarketingPreviewTmptFiles)
                for templateName in emailMarketingPreviewTmptFiles:
                    localFilenameWithPath = 'static/common/email_templates/'+str(templateName)
                    # html file content 
                    localEmailMarketingHtmlFile = render_to_string(localFilenameWithPath)
                    # ends here ~ html file content

                    # set file name without extension 
                    localTmptWithoutExt = templateName.split('.html')
                    localTmptWithoutExt = localTmptWithoutExt[0]
                    # ends here ~ set file name without extension

                    # set value into emailMarketingPreviewTmpDict dictionary
                    emailMarketingPreviewTmpDict['filename'] = templateName
                    emailMarketingPreviewTmpDict['preview_html_template'] = localEmailMarketingHtmlFile 
                    emailMarketingPreviewTmpDict['filename_without_ext'] = localTmptWithoutExt
                    # ends here ~ set value into emailMarketingPreviewTmpDict dictionary

                    # append data into list
                    emailMarketingPreviewTmptList.append(emailMarketingPreviewTmpDict.copy())
                    # ends here ~ append data into list

                    # empty emailMarketingPreviewTmpDict dictionary
                    emailMarketingPreviewTmpDict['filename'] = ''
                    emailMarketingPreviewTmpDict['preview_html_template'] = ''
                    emailMarketingPreviewTmpDict['filename_without_ext'] = ''
                    # ends here ~ empty emailMarketingPreviewTmpDict dictionary


                # ends here ~ for loop on email marketing preview template file names (emailMarketingPreviewTmptFiles)

                # get required data from articles2 table
                articles2FilterData = Articles2.objects.get(id=event_id)
                articlesTicketUrl = articles2FilterData.ticket_url
                eventName = articles2FilterData.event_name
                # ends here ~ get required data from articles2 table

                # html_message = render_to_string('static/common/sms_marketing_success.html')
                return render(request, "dashboard/email-marketing/email_campaign_listing.html",{'emailMarketingTmptList':emailMarketingPreviewTmptList, 'event_id':event_id,'campaignDetails':campaignDetailsList, 'total_campaign':cammpaignTemplateLen, 'emailCreditLeft':emailCreditLeft,'event_name':eventName})
            except Exception as e:
                print('error in email_campaign_listing function | GET request >> ',e)
        # ends here ~ code for get required

        # code for post request
        if request.method == 'POST':
            try:
                pass
            except Exception as e:
                pass
        # ends here ~ code for post required
    except Exception as e:
        pass


def select_email_marketing_template(request, event_id):
    try:
        # code for get request
        if request.method == 'GET':
            try:
                if 'userid' not in request.session.keys():
                    return redirect('/live/login')

                 #####################################################
                # new modified code ~ december 21 2019

                # Code Block for Fetch Campaign Information
                campaignTemplatesFilter = CampaignTemplates.objects.filter(event_id=event_id,template_type='email').values('created_on','scheduled_on','status','template_id')
                cammpaignTemplateLen = len(campaignTemplatesFilter)
                campaignDetailsData = list(campaignTemplatesFilter)

                
                campaignDetailsList = []
                # totalEmailCount = 0
                for campaign_details in campaignDetailsData:
                    campaignDetailsDict = {'created_on':'','scheduled_on':'','status':'','credit_use':''}
                    campaignDetailsDict['created_on']=campaign_details['created_on']
                    campaignDetailsDict['scheduled_on']=campaign_details['scheduled_on']
                    campaignDetailsDict['status']=campaign_details['status']

                    ###################################################
                    # code block for get total email count
                    campaignTemplateId = campaign_details['template_id']
                    emailCount = CampaignStatus.objects.filter(campaign_id=campaignTemplateId).count()
                    # totalEmailCount+=emailCount
                    campaignDetailsDict['credit_use'] = emailCount
                    # ends here ~ code block for get total email count
                    ###################################################

                    campaignDetailsList.append(campaignDetailsDict.copy())
                # ends here ~ Code Block for Fetch Campaign Information

                # filter required data from StatusPromotionTicketing table
                statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package','email_credit')
                statusPromoList = list(statusPromoFilter)
                eventLeadsPackageVal = statusPromoList[0]['leads_package']
                emailCreditVal = statusPromoList[0]['email_credit']
                # ends here ~ filter required data from StatusPromotionTicketing table

                # set total valid email limit
                # filterFinanceStdChrge = FinanceStandardCharges.objects.filter(charges_id=eventLeadsPackageVal).values('email')
                # if(len(filterFinanceStdChrge) == 0):
                #     totalEmailCountUpto = 1000
                # else:
                #     totalEmailVal = filterFinanceStdChrge[0]['email']
                #     if(totalEmailVal == 0):
                #         totalEmailCountUpto = 1000
                #     else:
                #         totalEmailCountUpto = filterFinanceStdChrge[0]['email']
                # ends here ~ set total valid email limit

                # total email credit left
                # emailCreditLeft = totalEmailCountUpto - totalEmailCount
                emailCreditLeft = emailCreditVal
                # ends here ~ total email credit left 


                # ends here ~ new modified code ~ december 21 2019
                #####################################################

                # read files name from folder
                emailMarketingPreviewTmpt = os.path.join(BASE_DIR, 'templates/static/common/email_templates')
                emailMarketingPreviewTmptFiles = [f for f in listdir(emailMarketingPreviewTmpt) if isfile(join(emailMarketingPreviewTmpt, f))]
                # ends here ~ read files name from folder
                
                # blank dict and list for preview email for showing in ui 
                emailMarketingPreviewTmpDict = {'filename':'','preview_html_template':'', 'filename_without_ext':''}
                emailMarketingPreviewTmptList = []
                # ends here ~ blank dict and list for preview email for showing in ui

                # for loop on email marketing preview template file names (emailMarketingPreviewTmptFiles)
                for templateName in emailMarketingPreviewTmptFiles:
                    localFilenameWithPath = 'static/common/email_templates/'+str(templateName)
                    # html file content 
                    localEmailMarketingHtmlFile = render_to_string(localFilenameWithPath)
                    # ends here ~ html file content

                    # set file name without extension 
                    localTmptWithoutExt = templateName.split('.html')
                    localTmptWithoutExt = localTmptWithoutExt[0]
                    # ends here ~ set file name without extension

                    # set value into emailMarketingPreviewTmpDict dictionary
                    emailMarketingPreviewTmpDict['filename'] = templateName
                    emailMarketingPreviewTmpDict['preview_html_template'] = localEmailMarketingHtmlFile 
                    emailMarketingPreviewTmpDict['filename_without_ext'] = localTmptWithoutExt
                    # ends here ~ set value into emailMarketingPreviewTmpDict dictionary

                    # append data into list
                    emailMarketingPreviewTmptList.append(emailMarketingPreviewTmpDict.copy())
                    # ends here ~ append data into list

                    # empty emailMarketingPreviewTmpDict dictionary
                    emailMarketingPreviewTmpDict['filename'] = ''
                    emailMarketingPreviewTmpDict['preview_html_template'] = ''
                    emailMarketingPreviewTmpDict['filename_without_ext'] = ''
                    # ends here ~ empty emailMarketingPreviewTmpDict dictionary


                # ends here ~ for loop on email marketing preview template file names (emailMarketingPreviewTmptFiles)

                # get required data from articles2 table
                articles2FilterData = Articles2.objects.get(id=event_id)
                articlesTicketUrl = articles2FilterData.ticket_url
                eventName = articles2FilterData.event_name
                # ends here ~ get required data from articles2 table

                # html_message = render_to_string('static/common/sms_marketing_success.html')
                return render(request, "dashboard/email-marketing/select_email_marketing_template.html",{'emailMarketingTmptList':emailMarketingPreviewTmptList, 'event_id':event_id,'campaignDetails':campaignDetailsList, 'total_campaign':cammpaignTemplateLen, 'emailCreditLeft':emailCreditLeft,'event_name':eventName})
            except Exception as e:
                print('error in select_email_marketing_template function | GET request >> ',e)
        # ends here ~ code for get required

        # code for post request
        if request.method == 'POST':
            try:
                pass
            except Exception as e:
                pass
        # ends here ~ code for post required
    except Exception as e:
        pass
# ends here ~ function for select template for email marketing

# function for intial email marketing form
@csrf_exempt
def email_marketing_initial_details(request, event_id, template_name):
    try:
        # get required data from articles2 table
        articles2FilterData = Articles2.objects.get(id=event_id)
        articlesTicketUrl = articles2FilterData.ticket_url
        eventName = articles2FilterData.event_name
        # ends here ~ get required data from articles2 table
        # get package id on basis of event id
        statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package','email_credit')
        statusPromoList = list(statusPromoFilter)
        emailCreditLeft = statusPromoList[0]['email_credit']
        # ends here ~ get package id on basis of event id

        if request.method == 'GET':
            if 'userid' not in request.session.keys():
                return redirect('/live/login')
            try:
                # get user id
                user_id = request.session['userid']
                # ends here ~ get user id
                
                # get data from short url tracker table
                urlShortnerFilter = ShortUrlTracker.objects.filter(event_id=event_id, source='email_marketing_organizer').values('short_url')
                # ends here ~ get data from UrlMap

                # code for handling short url functionality
                if (len(urlShortnerFilter) == 0):
                    shortUrl = url_shortner.create(event_id,articlesTicketUrl,'email_marketing_organizer')
                elif(len(urlShortnerFilter) == 1):
                    urlShortnerFilter_new = ShortUrlTracker.objects.filter(event_id=event_id, original_url=articlesTicketUrl, source='email_marketing_organizer').values('short_url')
                    if(len(urlShortnerFilter_new) == 1):
                        shortUrl = list(urlShortnerFilter_new)[0]['short_url']
                    elif(len(urlShortnerFilter_new) == 0):
                        ShortUrlTracker.objects.filter(event_id=event_id, source='email_marketing_organizer').update(original_url=articlesTicketUrl)
                        shortUrl = list(urlShortnerFilter)[0]['short_url']
                # ends here ~ code for handling short url functionality

                # make short url
                shortTicketUrl = 'https://' + request.get_host() + '/rcss/'+shortUrl
                # ends here ~ make short url

                # query for check is there any predefined template exists 
                compaignTemplateFilter = CampaignTemplates.objects.filter(user_id=user_id,is_standard=1,template_type='email').values()
                # ends here ~ query for check is there any predefined template exists

                # set default string for template 
                if(len(compaignTemplateFilter) > 0):
                    compaignTemplateList = list(compaignTemplateFilter)
                    compaignTemplateList = compaignTemplateList[-1]
                    template_email_data = compaignTemplateList['template_msg']
                    is_standard_exists = 'true'
                    template_subject = compaignTemplateList['template_subject']
                    template_image = compaignTemplateList['template_image']
                else:
                    template_email_data = ''
                    is_standard_exists = 'false'
                    template_subject = ''
                    template_image = ''
                # ends here ~ set default string for template

                ##############################################
                #
                ##############################################

                return render(request, "dashboard/email-marketing/email_marketing_initial_details.html", {'event_id':event_id, 'short_ticket_url':shortTicketUrl,'template_email_data':template_email_data,'template_subject':template_subject,'template_image':template_image,'is_standard_exists':is_standard_exists,'event_name':eventName,'emailCreditLeft':emailCreditLeft})     
            except Exception as e:
                print('error in GET request | email_marketing_initial_details function >> ',e)

        if request.method == 'POST':
            try:
                if 'userid' not in request.session.keys():
                    return redirect('/live/login')
                user_id = request.session['userid']
                
                # read request data
                requestData = request.POST['payload']
                # requestDataDecode = requestData.decode('utf8').replace("'", '"')
                requestDataJson = json.loads(requestData)
                # requestDataJson = request.POST['payload']
                # ends here ~ read request data

                # set data into variables 
                template_msg = requestDataJson['template_msg']
                template_link = requestDataJson['template_link']
                template_msg_with_link = template_msg
                template_msg_with_link += ' '
                template_msg_with_link += template_link
                is_standard = requestDataJson['is_standard']
                template_previous_img = requestDataJson['template_previous_img']
                template_subject = requestDataJson['template_subject']
                template_type = 'email'
                functionType = requestDataJson['functionType']
                htmlFileName = str(template_name)+'.html'
                htmlFilePath = 'static/common/email_templates/dynamic/'+str(htmlFileName)
                # ends here ~ set data into variables

                ####################################
                if functionType == 'previewData':
                    # function for show preview of email marketing
                    generateEmailMarketingPreview = render_to_string(htmlFilePath,
                        {
                        'event_name': eventName,
                        'template_msg': template_msg,
                        'short_ticket_url': template_link,
                    })

                    # return required response to ajax to show preview of email marketing
                    messageData = {'message': 'Show SMS Template Preview', 'responseType': 'success', 'messageType': 'success', 'url': '', 'data':generateEmailMarketingPreview}
                    return HttpResponse(json.dumps(messageData))
                    # ends here ~ return required response to ajax to show preview of email marketing

                    # ends here ~ function for show preview of email marketing
                else:
                    # function for save data of email marketing into required db table's 
                    fileName = ''
                    if(request.FILES.get('file') == None):
                        # code works if no new file is added via UI
                        if (template_previous_img != ''):

                            emailCampaignImgPathOld = MEDIA_DIR + "/email-marketing-campaign/" + str(template_previous_img)

                            if(os.path.exists(emailCampaignImgPathOld)):
                                # if file exists in directory or folder
                                
                                # set file name and file path
                                fileExt = template_previous_img.split('.')[-1]
                                fileName = str(uuid.uuid4())+'.'+str(fileExt)
                                emailCampaignImgPathNew = MEDIA_DIR + "/email-marketing-campaign/" + str(fileName)
                                # ends here ~ set file name and file path

                                shutil.copy(emailCampaignImgPathOld,emailCampaignImgPathNew )
                                # ends here ~ if file exists in directory
                        # ends here ~ code works if no new file is added via UI
                    else:
                        # code for save new image
                        emailContentImg = request.FILES['file']
                        fileExt = emailContentImg.name.split('.')[-1]
                        fileName = str(uuid.uuid4())+'.'+str(fileExt)
                        emailCampaignImgPath = MEDIA_DIR + "/email-marketing-campaign/" + str(fileName)
                        default_storage.save(emailCampaignImgPath, ContentFile(emailContentImg.read()))
                        # ends here ~ code for save new image

                    # code for save data in table
                    campaignTemplatesObject = CampaignTemplates.objects.create(user_id=user_id,predefined_template_id=template_name,template_type='email',template_msg=template_msg,template_link=template_link,is_standard=is_standard,status='incomplete',created_on=datetime.now(),scheduled_on=datetime.now(),template_subject=template_subject,template_image=fileName,event_id=event_id)
                    # ends here ~ code for save data in table

                    # return data to ajax on save data
                    filterTempleteId = campaignTemplatesObject.template_id
                    nextPageUrl = '/live/dashboard/email-marketing-advance-details/' + str(event_id)+'/'+str(filterTempleteId)
                    messageData = {'message': 'Email Template successfully Saved', 'responseType': 'success', 'messageType': 'success', 'url': nextPageUrl, 'event_id': event_id}
                    return HttpResponse(json.dumps(messageData))
                    # ends here ~  return data to ajax on save data

                    # ends here ~ function for save data of email marketing into required db table's
                ####################################

            except Exception as e:
                print('error in POST request | email_marketing_initial_details function >> ',e)
    except Exception as e:
        print('error in email_marketing_initial_details function >> ',e)
# ends here ~ function for intial email marketing form

# function
def addEmailCampaignDataInLeads(user_id, event_id, submitType, contactCsvFile, isAddLeads):
    try:
        # get package id on basis of event id
        statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package','email_credit')
        statusPromoList = list(statusPromoFilter)
        emailCreditLeft = statusPromoList[0]['email_credit']
        # ends here ~ get package id on basis of event id

        # fetch and set category id and topic id
        filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
        categEvents = list(filterCategEvents)[0]
        catId = categEvents['category_id']
        topicId = categEvents['topic_id']
        # ends here ~ fetch and set category id and topic id

        # fetch city name from articles 2 table
        filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
        articleCityName = list(filterArtiData)[0]['city']
        articleEventName = list(filterArtiData)[0]['event_name']
        # ends here ~ fetch city name from articles 2 table

        # read file and other data
        decodedCsvFile = contactCsvFile
        # ends here ~ read file and other data


        duplicateRecords = 0
        successfulAddedRecords = 0
        failedRecords = 0
        currentRow = 1
        failedRowList = []
        loop_count = 0
        totalValidContacts = 0

        ###################################################
        
        csv_list = [r[0:3] for r in csv.reader(decodedCsvFile)]
        email_list = []
        for x in csv_list[1:]:
            try:
                email_list.append(x[1])
            except:
                pass
        
        emailRegex=re.compile("^[a-zA-Z0-9.!#$%&’*+\\/=?^_`{|}~-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)*$")
        for email in email_list:
            emailValid = emailRegex.match(email)
            if(emailValid != None):
                totalValidContacts+=1
                leadsFilterData = Leads.objects.filter(user_id=user_id, email=email,city=articleCityName,category=catId)
                if not leadsFilterData:
                    # save rsvp personal data to additional leads table
                    # if isAddLeads == True:
                    Leads.objects.create(name='',email=email,contact='',category=catId,sub_category=topicId,city=articleCityName,user_id=user_id)
                    loop_count+=1
                    successfulAddedRecords+=1
                    # ends here ~ save rsvp personal data to additional leads table
                else:
                    duplicateRecords+=1
            else:
                failedRecords+=1
        
        

        #####################################################
        # emailSentContactCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(email='').values_list('email').distinct().count()
        emailSentContactCount = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(email='').values_list('email').distinct().count()
        totalContactCount = emailSentContactCount
        if isAddLeads == False:
            newContactCount = successfulAddedRecords
            totalNewCreditRequire = newContactCount - emailCreditLeft

            if(emailCreditLeft < totalContactCount):
                # updated data dict
                csvContactUploadResult = {'duplicateRecords':duplicateRecords,'totalValidContacts':totalValidContacts,'failedRecords':failedRecords,'successfulAddedRecords':successfulAddedRecords,'emailCreditLeft':emailCreditLeft,'newContactCount':newContactCount,'newCreditRequire':totalNewCreditRequire,'emailSentContactCount':emailSentContactCount}
                # ends here ~ updated data dict
                textMessage = 'You only have '+str(emailCreditLeft)+' credits and total contacts are '+str(totalContactCount)+', would you like to purchase more credits or restrict to the available credits'
                messageData = {'message': textMessage, 'responseType': 'success', 'messageType': 'error', 'data':csvContactUploadResult}
                return HttpResponse(json.dumps(messageData))
            else:
                return True
                # # updated data dict
                # csvContactUploadResult = {'duplicateRecords':duplicateRecords,'totalValidContacts':totalValidContacts,'failedRecords':failedRecords,'successfulAddedRecords':successfulAddedRecords,'emailCreditLeft':emailCreditLeft,'newContactCount':newContactCount,'newCreditRequire':totalNewCreditRequire,'emailSentContactCount':emailSentContactCount}
                # # ends here ~ updated data dict
                # textMessage = 'You only have '+str(emailCreditLeft)+' credits and total contacts are '+str(totalContactCount)+', would you like to purchase more credits or restrict to the available credits'
                # messageData = {'message': textMessage, 'responseType': 'success', 'messageType': 'success', 'data':csvContactUploadResult}
                # return HttpResponse(json.dumps(messageData))
        else:

            #@author Shubham ~ modify code ~ december 19 2019
            csvContactUploadResult = {'duplicateRecords':duplicateRecords,'totalValidContacts':totalValidContacts,'failedRecords':failedRecords,'successfulAddedRecords':successfulAddedRecords,'emailSentContactCount':emailSentContactCount}  
            messageData = {'message': '', 'responseType': 'success', 'messageType': 'success', 'data':csvContactUploadResult}
            return HttpResponse(json.dumps(messageData))
            
    except Exception as e:
        print('error in addEmailCampaignDataInLeads function >> ',e)
# ends here ~ function

# function for advance email marketing form
@csrf_exempt
def email_marketing_advance_details(request, event_id,campaign_template_id):
    try:
        template_id = campaign_template_id
        if request.method == 'GET':
            if 'userid' not in request.session.keys():
                return redirect('/live/login')
            try:
                # get user id
                user_id = request.session['userid']
                # ends here ~ get user id

                # get required data from articles2 table
                articles2FilterData = Articles2.objects.get(id=event_id)
                eventEndDate = articles2FilterData.edate
                eventName = articles2FilterData.event_name
                # ends here ~ get required data from articles2 table

                # fetch and set category id and topic id
                filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
                categEvents = list(filterCategEvents)[0]
                catId = categEvents['category_id']
                topicId = categEvents['topic_id']
                # ends here ~ fetch and set category id and topic id

                # fetch city name from articles 2 table
                filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
                articleCityName = list(filterArtiData)[0]['city']
                articleEventName = list(filterArtiData)[0]['event_name']
                # ends here ~ fetch city name from articles 2 table

                # leads count
                # print(Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(email='').values_list('email').distinct().values('email'))
                # leadCount = CampaignStatus.objects.filter(campaign_id=template_id).count()
                # leadCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(email='').count()
                leadCount = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(email='').values_list('email').distinct().count()
                # ends here ~ leads count

                return render(request, "dashboard/email-marketing/email_marketing_advance_details.html", {'event_id':event_id,'template_id':template_id,'event_end_date':eventEndDate, 'contactCount':leadCount, 'event_name':eventName})     
            except Exception as e:
                print('error in GET request | email_marketing_advance_details function >> ',e)

        if request.method == 'POST':
            try:
                if 'userid' not in request.session.keys():
                    return redirect('/live/login')
                user_id = request.session['userid']
                
                # read request data
                event_id = request.POST['event_id']
                submitType = request.POST['submitType']
                contactCsvFile = request.FILES['file']
                decodedCsvFile = contactCsvFile.read().decode('utf-8').splitlines()
                # ends here ~ read request data

                if submitType == 'normalSubmit':
                    checkUserEmailCredit = addEmailCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, False)
                    if checkUserEmailCredit == True:
                        return addEmailCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, True)
                    else:
                        return checkUserEmailCredit
                else:
                    return addEmailCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, True)

                # ends here ~ store values into db upto totalEmailVal contacts (if leads_package!=0)

            except Exception as e:
                print('error in POST request | email_marketing_advance_details function >> ',e)
    except Exception as e:
        print('error in email_marketing_advance_details function >> ',e)

@csrf_exempt
def email_marketing_advance_details_scheduling(request, event_id,campaign_template_id):
    try:
        template_id = campaign_template_id
        if request.method == 'GET':
            if 'userid' not in request.session.keys():
                return redirect('/live/login')
            try:
                # get user id
                user_id = request.session['userid']
                # ends here ~ get user id

                # get required data from articles2 table
                articles2FilterData = Articles2.objects.get(id=event_id)
                eventEndDate = articles2FilterData.edate
                eventName = articles2FilterData.event_name
                # ends here ~ get required data from articles2 table

                # fetch and set category id and topic id
                filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
                categEvents = list(filterCategEvents)[0]
                catId = categEvents['category_id']
                topicId = categEvents['topic_id']
                # ends here ~ fetch and set category id and topic id

                # fetch city name from articles 2 table
                filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
                articleCityName = list(filterArtiData)[0]['city']
                articleEventName = list(filterArtiData)[0]['event_name']
                # ends here ~ fetch city name from articles 2 table

                # leads count
                # print(Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(email='').values_list('email').distinct().values('email'))
                # leadCount = CampaignStatus.objects.filter(campaign_id=template_id).count()
                # leadCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(email='').count()
                leadCount = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(email='').values_list('email').distinct().count()
                # ends here ~ leads count

                return render(request, "dashboard/email-marketing/email_marketing_advance_details_scheduling.html", {'event_id':event_id,'template_id':template_id,'event_end_date':eventEndDate, 'contactCount':leadCount, 'event_name':eventName})     
            except Exception as e:
                print('error in GET request | email_marketing_advance_details_scheduling function >> ',e)

        if request.method == 'POST':
            try:
                if 'userid' not in request.session.keys():
                    return redirect('/live/login')
                user_id = request.session['userid']
                
                # read request data
                event_id = request.POST['event_id']
                submitType = request.POST['submitType']
                contactCsvFile = request.FILES['file']
                decodedCsvFile = contactCsvFile.read().decode('utf-8').splitlines()
                # ends here ~ read request data

                if submitType == 'normalSubmit':
                    checkUserEmailCredit = addEmailCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, False)
                    if checkUserEmailCredit == True:
                        return addEmailCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, True)
                    else:
                        return checkUserEmailCredit
                else:
                    return addEmailCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, True)

                # ends here ~ store values into db upto totalEmailVal contacts (if leads_package!=0)

            except Exception as e:
                print('error in POST request | email_marketing_advance_details_scheduling function >> ',e)
    except Exception as e:
        print('error in email_marketing_advance_details_scheduling function >> ',e)

@csrf_exempt
def email_marketing_success_page(request, event_id,campaign_template_id):
    try:
        template_id = campaign_template_id
        if request.method == 'GET':
            if 'userid' not in request.session.keys():
                return redirect('/live/login')
            try:
                # get user id
                user_id = request.session['userid']
                # ends here ~ get user id

                # get required data from articles2 table
                articles2FilterData = Articles2.objects.get(id=event_id)
                eventEndDate = articles2FilterData.edate
                eventName = articles2FilterData.event_name
                # ends here ~ get required data from articles2 table

                # fetch and set category id and topic id
                filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
                categEvents = list(filterCategEvents)[0]
                catId = categEvents['category_id']
                topicId = categEvents['topic_id']
                # ends here ~ fetch and set category id and topic id

                # fetch city name from articles 2 table
                filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
                articleCityName = list(filterArtiData)[0]['city']
                articleEventName = list(filterArtiData)[0]['event_name']
                # ends here ~ fetch city name from articles 2 table

                # leads count
                # print(Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(email='').values_list('email').distinct().values('email'))
                # leadCount = CampaignStatus.objects.filter(campaign_id=template_id).count()
                # leadCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(email='').count()
                leadCount = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(email='').values_list('email').distinct().count()
                # ends here ~ leads count

                return render(request, "dashboard/email-marketing/email_marketing_success_page.html", {'event_id':event_id,'template_id':template_id,'event_end_date':eventEndDate, 'contactCount':leadCount, 'event_name':eventName})     
            except Exception as e:
                print('error in GET request | email_marketing_success_page function >> ',e)

        if request.method == 'POST':
            try:
                if 'userid' not in request.session.keys():
                    return redirect('/live/login')
                user_id = request.session['userid']
                
                # read request data
                event_id = request.POST['event_id']
                submitType = request.POST['submitType']
                contactCsvFile = request.FILES['file']
                decodedCsvFile = contactCsvFile.read().decode('utf-8').splitlines()
                # ends here ~ read request data

                if submitType == 'normalSubmit':
                    checkUserEmailCredit = addEmailCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, False)
                    if checkUserEmailCredit == True:
                        return addEmailCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, True)
                    else:
                        return checkUserEmailCredit
                else:
                    return addEmailCampaignDataInLeads(user_id, event_id, submitType, decodedCsvFile, True)

                # ends here ~ store values into db upto totalEmailVal contacts (if leads_package!=0)

            except Exception as e:
                print('error in POST request | email_marketing_success_page function >> ',e)
    except Exception as e:
        print('error in email_marketing_success_page function >> ',e)
        
# ends here ~ function for advance email marketing form

# # function for advance email marketing form
# @csrf_exempt
# def email_marketing_advance_details(request, event_id,campaign_template_id):
#     try:
#         template_id = campaign_template_id
#         if request.method == 'GET':
#             if 'userid' not in request.session.keys():
#                 return redirect('/live/login')
#             try:
#                 # get user id
#                 user_id = request.session['userid']
#                 # ends here ~ get user id

#                 # get required data from articles2 table
#                 articles2FilterData = Articles2.objects.get(id=event_id)
#                 eventEndDate = articles2FilterData.edate
#                 eventName = articles2FilterData.event_name
#                 # ends here ~ get required data from articles2 table

#                 # fetch and set category id and topic id
#                 filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
#                 categEvents = list(filterCategEvents)[0]
#                 catId = categEvents['category_id']
#                 topicId = categEvents['topic_id']
#                 # ends here ~ fetch and set category id and topic id

#                 # fetch city name from articles 2 table
#                 filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
#                 articleCityName = list(filterArtiData)[0]['city']
#                 articleEventName = list(filterArtiData)[0]['event_name']
#                 # ends here ~ fetch city name from articles 2 table

#                 # leads count
#                 # leadCount = CampaignStatus.objects.filter(campaign_id=template_id).count()
#                 leadCount = Leads.objects.filter(city=articleCityName,category=catId).exclude(email='').count()
#                 # ends here ~ leads count

#                 return render(request, "dashboard/email-marketing/email_marketing_advance_details.html", {'event_id':event_id,'template_id':template_id,'event_end_date':eventEndDate, 'contactCount':leadCount, 'event_name':eventName})     
#             except Exception as e:
#                 print('error in GET request | email_marketing_advance_details function >> ',e)

#         if request.method == 'POST':
#             try:
#                 if 'userid' not in request.session.keys():
#                     return redirect('/live/login')
#                 user_id = request.session['userid']
#                 # read request data

#                 event_id = request.POST['event_id']

#                 # get package id on basis of event id
#                 statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package')
#                 statusPromoList = list(statusPromoFilter)
#                 eventLeadsPackageVal = statusPromoList[0]['leads_package']
#                 # ends here ~ get package id on basis of event id

#                 # fetch and set category id and topic id
#                 filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
#                 categEvents = list(filterCategEvents)[0]
#                 catId = categEvents['category_id']
#                 topicId = categEvents['topic_id']
#                 # ends here ~ fetch and set category id and topic id

#                 # fetch city name from articles 2 table
#                 filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
#                 articleCityName = list(filterArtiData)[0]['city']
#                 articleEventName = list(filterArtiData)[0]['event_name']
#                 # ends here ~ fetch city name from articles 2 table

#                 # read file and other data
#                 contactCsvFile = request.FILES['file']
#                 decodedCsvFile = contactCsvFile.read().decode('utf-8').splitlines()
#                 # ends here ~ read file and other data

#                 # set total valid email limit
#                 filterFinanceStdChrge = FinanceStandardCharges.objects.filter(charges_id=eventLeadsPackageVal).values('email')
#                 if(len(filterFinanceStdChrge) == 0):
#                     totalEmailCountUpto = 1001
#                 else:
#                     totalEmailVal = filterFinanceStdChrge[0]['email']
#                     if(totalEmailVal == 0):
#                         totalEmailCountUpto = 1001
#                     else:
#                         totalEmailCountUpto = filterFinanceStdChrge[0]['email'] + 1
#                 # ends here ~ set total valid email limit

#                 ######################################################
#                 # @author Shubham ~ modify code ~ december 20 2019

#                 duplicateRecords = 0
#                 successfulAddedRecords = 0
#                 failedRecords = 0
#                 currentRow = 1
#                 failedRowList = []
#                 loop_count = 0
#                 totalValidContacts = 0

#                 for email_list in (r[0:3] for r in csv.reader(decodedCsvFile)):
#                     emailRegex=re.compile("^[a-zA-Z0-9.!#$%&’*+\\/=?^_`{|}~-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)*$")
#                     for email in email_list:
#                         emailValid = emailRegex.match(email)
#                         if(emailValid != None):
#                             totalValidContacts+=1
#                             leadsFilterData = Leads.objects.filter(email=email,city=articleCityName,category=catId)
#                             if not leadsFilterData:
#                                 # save rsvp personal data to additional leads table
#                                 Leads.objects.create(name='',email=email,contact='',category=catId,sub_category=topicId,city=articleCityName,user_id=user_id)
#                                 loop_count+=1
#                                 successfulAddedRecords+=1
#                                 # ends here ~ save rsvp personal data to additional leads table
#                             else:
#                                 duplicateRecords+=1
#                         else:
#                             failedRecords+=1

#                 # return data to ajax on save data

#                 csvContactUploadResult = {'duplicateRecords':duplicateRecords,'totalValidContacts':totalValidContacts,'failedRecords':failedRecords,'successfulAddedRecords':successfulAddedRecords}  
#                 messageData = {'message': '', 'responseType': 'success', 'messageType': 'success', 'data':csvContactUploadResult}
#                 return HttpResponse(json.dumps(messageData))

#                 # if loop_count == 0 and duplicateRecords == 0:
#                 #     messageData = {'message': 'No contact synced. All emails seem invalid.', 'responseType': 'success', 'messageType': 'error'}
#                 # elif loop_count == 0 and duplicateRecords > 0:
#                 #     messageData = {'message': 'No contact synced. '+str(duplicateRecords)+' duplicate records found', 'responseType': 'success', 'messageType': 'error'}
#                 # elif loop_count > 0:
#                 #     messageData = {'message': 'All valid contacts synced', 'responseType': 'success', 'messageType': 'success'}
#                 # return HttpResponse(json.dumps(messageData))
#                 # ends here ~ return data to ajax on save data

#                 # ends here ~ @author Shubham ~ modify code ~ december 20 2019
#                 ##########################################

#                 # ends here ~ store values into db upto totalEmailVal contacts (if leads_package!=0)

#             except Exception as e:
#                 print('error in POST request | email_marketing_advance_details function >> ',e)
#     except Exception as e:
#         print('error in email_marketing_advance_details function >> ',e)

# # ends here ~ function for advance email marketing form

# save scheduled values email marketing
@csrf_exempt
def email_marketing_schedule(request):
    try:
        if request.method == 'GET':
            if 'userid' not in request.session.keys():
                return redirect('/live/login')
        if request.method == 'POST':
            try:
                if 'userid' not in request.session.keys():
                    return redirect('/live/login')
                user_id = request.session['userid']
                # read request data
                requestData = request.body
                requestDataDecode = requestData.decode('utf8').replace("'", '"')
                requestDataJson = json.loads(requestDataDecode)
                # ends here ~ read request data

                # set value into variables
                event_id = requestDataJson['event_id']
                template_id = requestDataJson['template_id']
                scheduled_on_date = requestDataJson['scheduled_on_date']
                scheduled_on_time = requestDataJson['scheduled_on_time']
                # ends here ~ set value into variables

                # update schedule datetime according to template id
                scheduledDateTime = datetime.strptime(scheduled_on_date +' '+scheduled_on_time, '%d/%m/%Y %I:%M %p')
                CampaignTemplates.objects.filter(template_id=template_id).update(scheduled_on=scheduledDateTime)
                # ends here ~ update schedule datetime according to template id

                # get package id on basis of event id
                statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package')
                statusPromoList = list(statusPromoFilter)
                eventLeadsPackageVal = statusPromoList[0]['leads_package']
                # ends here ~ get package id on basis of event id

                # set total valid email limit
                # filterFinanceStdChrge = FinanceStandardCharges.objects.filter(charges_id=eventLeadsPackageVal).values('email')
                # if(len(filterFinanceStdChrge) == 0):
                #     totalemailCountUpto = 1001
                # else:
                #     totalemailVal = filterFinanceStdChrge[0]['email']
                #     if(totalemailVal == 0):
                #         totalemailCountUpto = 1001
                #     else:
                #         totalemailCountUpto = filterFinanceStdChrge[0]['email'] + 1
                # ends here ~ set total valid email limit

                statusPromoFilter = StatusPromotionTicketing.objects.get(event_id=event_id)
                newTotalCredits = statusPromoFilter.email_credit
                totalemailCountUpto = newTotalCredits

                # fetch and set category id and topic id
                filterCategEvents = CategorizedEvents.objects.filter(event_id=event_id).values('category_id','topic_id')
                categEvents = list(filterCategEvents)[0]
                catId = categEvents['category_id']
                topicId = categEvents['topic_id']
                # ends here ~ fetch and set category id and topic id

                # fetch city name from articles 2 table
                filterArtiData = Articles2.objects.filter(id=event_id).values('city','event_name')
                articleCityName = list(filterArtiData)[0]['city']
                articleEventName = list(filterArtiData)[0]['event_name']
                # ends here ~ fetch city name from articles 2 table

                # copy data from leads table to campaign status table
                orignalTotalemailCountUpto = totalemailCountUpto
                # leadsFilterData = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId,sub_category=topicId).order_by('-id')[:orignalTotalemailCountUpto].values()
                leadsFilterData = Leads.objects.filter(user_id=user_id,city=articleCityName,category=catId).exclude(email='').values_list('email').distinct().order_by('-id')[:orignalTotalemailCountUpto].values()
                leadsFilterList = list(leadsFilterData)
                loop_count=0

                # loop on Leads table last "orignalTotalemailCountUpto" rows filter data 
                for leadsData in leadsFilterList:
                    contactEmail = leadsData['email']
                    if contactEmail != '' and contactEmail != None:
                        # if contact email field is not empty
                        campaignStatusFilter = CampaignStatus.objects.filter(contact=contactEmail,campaign_id=template_id).values()
                        if(len(campaignStatusFilter) == 0):
                            # if contact is not already stored in CampaignStatus table with same campaign_id 
                            if loop_count == totalemailCountUpto:
                                break
                            CampaignStatus.objects.create(campaign_id=template_id, contact=contactEmail,contact_type='email',created_on=datetime.now(),updated_on=datetime.now(),status='scheduled')
                            loop_count+=1
                # ends here ~ loop on Leads table last "orignalTotalemailCountUpto" rows filter data

                # ends here ~ copy data from leads table to campaign status table

                # update StatusPromotionTicketing Table
                leftEmailCredit = newTotalCredits - loop_count
                if leftEmailCredit < 0:
                    leftEmailCredit = 0
                StatusPromotionTicketing.objects.filter(event_id=event_id).update(email_credit=leftEmailCredit)
                # ends here ~ update StatusPromotionTicketing Table

                # required data for ajax response
                schedule_data = {}
                campaignTemplatesFilter = CampaignTemplates.objects.get(template_id=template_id)
                templateMsg = campaignTemplatesFilter.template_msg
                templateImage = campaignTemplatesFilter.template_image
                templateImageWithPath = "/media/email-marketing-campaign/" + str(templateImage)
                htmlFileName = str(campaignTemplatesFilter.predefined_template_id)+'.html'
                htmlFilePath = 'static/common/email_templates/dynamic/'+str(htmlFileName)
                # remove link from templateMsg field
                templateMsg = templateMsg.split('http')
                templateMsg = templateMsg[0]
                # ends here  ~ remove link from templateMsg field
                templateLink = campaignTemplatesFilter.template_link
                leadContactCount = CampaignStatus.objects.filter(campaign_id=template_id).exclude(contact='').count()
                # leadContactCount = Leads.objects.filter(user_id=user_id).count()

                
                generateEmailMarketingPreview = render_to_string(htmlFilePath,
                    {
                    'event_name': articleEventName,
                    'template_msg': templateMsg,
                    'short_ticket_url': templateLink,
                    'template_image_with_path':templateImageWithPath
                })

                schedule_data['date_time'] = str(scheduled_on_date +' '+scheduled_on_time)
                schedule_data['templateMsg'] = templateMsg
                schedule_data['templateLink'] = templateLink
                schedule_data['totalContactCount'] = leadContactCount
                schedule_data['email_campaign_email_html'] = generateEmailMarketingPreview
                # ends here ~ required data for ajax response 

                # get user email
                filterUserData = Users.objects.get(id = user_id)
                organizerEmail = filterUserData.user
                # ends here ~ get user email

                # send email on completion of email marketing campaign
                # subject = 'Congratulations! New email Marketing Campaign Created Successfully'
                # email_from = conf_settings.EMAIL_HOST_USER
                # recipient_list = [organizerEmail]
                # html_message = render_to_string('static/common/email_marketing_success.html',
                #     {
                #     'campaign_scheduled_date_time': schedule_data['date_time'],
                #     'campaign_total_contacts': schedule_data['totalContactCount'],
                #     'campaign_message': schedule_data['templateMsg'],
                #     'campaign_short_link': schedule_data['templateLink'],
                #     'event_name': articleEventName
                # })
                # msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'track@ercess.com'})
                # msg.content_subtype = "html"
                # msg.send(fail_silently=False)
                # ends here ~ send email on completion of email marketing campaign

                # return data to ajax after save data
                messageData = {'message': 'All Contacts Uploaded', 'responseType': 'success', 'messageType': 'success','data':schedule_data}
                return HttpResponse(json.dumps(messageData))
                # ends here ~ return data to ajax after save data

            except Exception as e:
                print('error in POST request | email_marketing_schedule_details function >> ',e)
    except Exception as e:
        print('error in email_marketing_schedule_details function >> ',e)
# ends here ~ save scheduled values email marketing



############ Expectation   ###################
class Expectation(View):
    template_name = "expectation.html"
    def get(self, request,event_id,booking_id):
    
        check_user = PackageSales.objects.get(booking_id = booking_id)
        # print(check_user,'===========')
        user_id = check_user.user_id
        user = Users.objects.get(id = user_id)
        email = user.user
        event = Articles2.objects.get(id = int(event_id))
        expectation = ExpectationsFeedbacks.objects.filter(event_id = event_id, email = email, booking_id = booking_id).exists()  

        if not expectation:
            expectation =  ExpectationsFeedbacks.objects.create(event_id = event_id, email = email, booking_id = booking_id, exp_mail_status = "page opend")
        return render(request,self.template_name,locals())

    def post(self, request, event_id,booking_id):
        # user_id = request.session.get('userid')
        email = request.POST.get('email')
        message = request.POST.get('message')
        check_user = PackageSales.objects.get(booking_id = booking_id)
        
        try:         
            user_id = check_user.user_id
            user = Users.objects.get(id = user_id)
            email = user.user
            users = Users.objects.get(user = email)
            first_name = users.firstname
            last_name = users.lastname
            expectation = ExpectationsFeedbacks.objects.filter(event_id = event_id, email = email, booking_id = booking_id)
            orgnizer = Articles2.objects.get(id = event_id)
            org_email = orgnizer.email_id_organizer 

            if message:
                expectation_msg = ExpectationsFeedbacks.objects.filter(event_id = event_id, email = email, booking_id = booking_id).update(expectation_msg = message, exp_email_attempts = 3, exp_mail_status = "customer replied")                                    
                subject = 'Check Expectation of your Event'
                link = conf_settings.BASE_URL + "/live/dashboard/expectation_list/" + str(event_id)
                email_from = conf_settings.EMAIL_HOST_USER
                recipient_list = [org_email]
                content_html = render_to_string('static/common/expection-mail.html', {'link':link,'firstname':first_name, 'lastname':last_name})
                send_mail(subject,message,email_from, recipient_list, html_message = content_html)
               
                messages.success(request,"SuccesFullly submit.")
                return HttpResponseRedirect('/live/expectation/'+ str(event_id) + '/' + str(booking_id))
            else:
                expectation_msg = ExpectationsFeedbacks.objects.filter(event_id = event_id, email = email, booking_id = booking_id).update(exp_email_attempts = 3, exp_mail_status = "customer replied")

                subject = 'Check Expectation of your Event'
                link = conf_settings.BASE_URL + "/live/dashboard/expectation_list/" + str(event_id)
                email_from = conf_settings.EMAIL_HOST_USER
                recipient_list = [org_email]
                content_html = render_to_string('static/common/expection-mail.html', {'link':link})
                send_mail(subject,message,email_from, recipient_list, html_message = content_html)
           
                messages.success(request,"SuccesFullly submit.")
                return HttpResponseRedirect('/live/expectation/'+ str(event_id)+ '/' + str(booking_id))
        except Exception as e:
            messages.error(request,"Invalid Email Address." + str(e))
            return HttpResponseRedirect('/live/expectation/'+ str(event_id) + '/' + str(booking_id))
    
####### feed backs ########
class FeedBacks(View):
    template_name = "feedback.html"
    def get(self, request,event_id, booking_id):
        check_user = PackageSales.objects.get(booking_id = booking_id)
        user_id = check_user.user_id
        user = Users.objects.get(id = user_id)
        email = user.user
        event = Articles2.objects.get(id = int(event_id))
       
        feed_back = ExpectationsFeedbacks.objects.filter(event_id = int(event_id), email = email, booking_id = booking_id).exists()  
        
        if not feed_back:
            feed_back =  ExpectationsFeedbacks.objects.create(event_id = int(event_id), email = email, booking_id = booking_id, feedback_mail_status = "page opend")
        return render(request,self.template_name,locals())


    def post(self,request,event_id, booking_id):
       
        rating = request.POST.get('ranting')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print(message,'>>>>>>>')
        check_user = PackageSales.objects.get(booking_id = booking_id)
       
        try:
            users = Users.objects.get(user = email)
            first_name = users.firstname
            last_name = users.lastname
            feed_back = ExpectationsFeedbacks.objects.filter(event_id = int(event_id), email = email, booking_id = booking_id)  
            print(feed_back,'>>>>>>>>')
            orgnizer = Articles2.objects.get(id = int(event_id))
            
            org_email = orgnizer.email_id_organizer 
            print(org_email,'>>>>>>>>') 
            # for i in feed_back:  
            if message != None:  
                feed_back = ExpectationsFeedbacks.objects.filter(event_id = int(event_id), email = email, booking_id = booking_id).update(feedback_msg = message, feedback_rating = rating, feedback_mail_attempts = 3, feedback_mail_status = "customer replied")            
                print(feed_back)
               
                subject = 'Check FeedBack of your Event'
                link = conf_settings.BASE_URL + "/live/dashboard/feed_back_list/" + str(event_id)
                
                
                recipient_list = [org_email]
                message = ""
                content_html = render_to_string('static/common/feedback-mail.html', {'link':link,'firstname':first_name, 'lastname':last_name})
                email_from = conf_settings.EMAIL_HOST_USER
                subject = "For FeedBack Message"
                send_mail(subject,message,email_from, recipient_list, html_message = content_html)
               
                messages.success(request,"SuccesFullly submit.")
                return HttpResponseRedirect('/live/feed_back/'+ str(event_id)+ '/' + str(booking_id))
                   
               
            else:
                feed_back = ExpectationsFeedbacks.objects.filter(event_id = int(event_id), email = email, booking_id = booking_id).update(feedback_rating = rating, feedback_mail_attempts = 3, feedback_mail_status = "customer replied")                
        
                subject = 'Check FeedBack of your Event'
                link = conf_settings.BASE_URL + "/live/dashboard/feed_back_list/" + str(event_id)
                
                recipient_list = [org_email]
                message = ""
                content_html = render_to_string('static/common/feedback-mail.html', {'link':link})
                email_from = conf_settings.EMAIL_HOST_USER
                subject = "For FeedBack Message"
                send_mail(subject,message,email_from, recipient_list, html_message = content_html)
                   
                messages.success(request,"SuccesFullly submit.")
                return HttpResponseRedirect('/live/feed_back/'+ str(event_id) + '/' + str(booking_id))

        except Exception as e:
            print(e)
            messages.error(request,"Invalid Email Address.")
            return HttpResponseRedirect('/live/feed_back/'+ str(event_id) + '/' + str(booking_id))

       
# toggle referral program
@csrf_exempt
def toggle_referral_program(request, event_id):
    try:
        if request.method == 'GET':
            if 'userid' not in request.session.keys():
                return redirect('/live/login')

            try:
                if StatusPromotionTicketing.objects.filter(event_id=event_id).exists():
                    statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('referrer_program_status')
                else:
                    return render(request, 'Ercesscorp/404.html', status=404)

                statusPromoDict = list(statusPromoFilter)[0]
                referrerProgramVal = statusPromoDict['referrer_program_status']

                # ReferrerCashbackInfo, ReferrerCashbackTokens, TicketSalesReference
                referrerTktSalesData = []

                tktSalesRefFilter = TicketSalesReference.objects.filter(event_id=event_id).values()
                tktSalesRefList = list(tktSalesRefFilter)
                tktSalesRefList = list({v['used_referred_code']:v for v in tktSalesRefList}.values())

                for tkt_sales_ref in tktSalesRefList:
                    usedReferredCode = tkt_sales_ref['used_referred_code']

                    tktSalesRefFilterInsideLoop = TicketSalesReference.objects.filter(used_referred_code=usedReferredCode).values()
                    tktSalesRefFilterLenInsideLoop = len(tktSalesRefFilterInsideLoop)

                    payableAmount = sum(item['cashback_to_process'] for item in list(tktSalesRefFilterInsideLoop))
                    
                    if(tktSalesRefFilterLenInsideLoop > 0):
                        refCashbackInfoFilter = ReferrerCashbackInfo.objects.filter(referrer_code=usedReferredCode).values('email_id','referrer_code')
                        refCashbackInfoList = list(refCashbackInfoFilter)
                        refCashbackInfoDict = refCashbackInfoList[0]
                        refInfoDict = refCashbackInfoDict
                        refInfoDict.update({'total_sales_count':tktSalesRefFilterLenInsideLoop, 'payable_amount':payableAmount})

                        referrerTktSalesData.append(refInfoDict.copy())

                return render(request, 'dashboard/referral-program.html',{'referrerProgramVal':referrerProgramVal, 'event_id':event_id, 'referrer_tkt_sales_data':referrerTktSalesData})
            except Exception as e:
                print('error in toggle_referral_program function | GET method >> ',e)
                return render(request, 'Ercesscorp/404.html', status=404)

        if request.method == 'POST':
            try:
                requestData = request.POST.dict()
                requestDict = requestData
                referrer_program_status = requestDict['referrer_program_status']
                StatusPromotionTicketing.objects.filter(event_id=event_id).update(referrer_program_status=referrer_program_status)
                return HttpResponseRedirect(reverse('dashboard:toggle-referral-program', args={event_id}))
            except Exception as e:
                return HttpResponseRedirect(reverse('dashboard:toggle-referral-program', args={event_id}))

    except Exception as e:
        print('error in toggle_referral_program function >> ',e)
        return render(request, 'Ercesscorp/404.html', status=404)
# ends here ~ toggle referral program

# affiliate marketing
@csrf_exempt
def affiliate_marketing(request, event_id): 
    try:
        if request.method == 'GET':
            if 'userid' not in request.session.keys():
                return redirect('/live/login')

            try:
                if StatusPromotionTicketing.objects.filter(event_id=event_id).exists():
                    statusPromoFilter = StatusPromotionTicketing.objects.filter(event_id=event_id).values('affiliate')
                else:
                    return render(request, 'Ercesscorp/404.html', status=404)

                statusPromoDict = list(statusPromoFilter)[0]
                affiliateVal = statusPromoDict['affiliate']

                # # ReferrerCashbackInfo, ReferrerCashbackTokens, TicketSalesReference
                # referrerTktSalesData = []

                # tktSalesRefFilter = TicketSalesReference.objects.filter(event_id=event_id).values()
                # tktSalesRefList = list(tktSalesRefFilter)
                # tktSalesRefList = list({v['used_referred_code']:v for v in tktSalesRefList}.values())

                # for tkt_sales_ref in tktSalesRefList:
                #     usedReferredCode = tkt_sales_ref['used_referred_code']

                #     tktSalesRefFilterInsideLoop = TicketSalesReference.objects.filter(used_referred_code=usedReferredCode).values()
                #     tktSalesRefFilterLenInsideLoop = len(tktSalesRefFilterInsideLoop)

                #     payableAmount = sum(item['cashback_to_process'] for item in list(tktSalesRefFilterInsideLoop))
                    
                #     if(tktSalesRefFilterLenInsideLoop > 0):
                #         refCashbackInfoFilter = ReferrerCashbackInfo.objects.filter(referrer_code=usedReferredCode).values('email_id','referrer_code')
                #         refCashbackInfoList = list(refCashbackInfoFilter)
                #         refCashbackInfoDict = refCashbackInfoList[0]
                #         refInfoDict = refCashbackInfoDict
                #         refInfoDict.update({'total_sales_count':tktSalesRefFilterLenInsideLoop, 'payable_amount':payableAmount})

                #         referrerTktSalesData.append(refInfoDict.copy())

                return render(request, 'dashboard/affiliate-marketing.html',{'affiliateVal':affiliateVal, 'event_id':event_id})
            except Exception as e:
                print('error in affiliate marketing function | GET method >> ',e)
                return render(request, 'Ercesscorp/404.html', status=404)

        if request.method == 'POST':
            try:
                requestData = request.POST.dict()
                requestDict = requestData
                affiliate_status = requestDict['affiliate_status']
                StatusPromotionTicketing.objects.filter(event_id=event_id).update(affiliate=int(affiliate_status))
                return HttpResponseRedirect(reverse('dashboard:affiliate-marketing', args={event_id}))
            except Exception as e:
                return HttpResponseRedirect(reverse('dashboard:affiliate-marketing', args={event_id}))

    except Exception as e:
        print('error in affiliate marketing function >> ',e)
        return render(request, 'Ercesscorp/404.html', status=404)
# ends here ~ affiliate marketing

# add more credit
def add_more_credit(request, event_id, purpose):
    try:
        ###########################################
        if request.method == 'GET':
            try:
                if 'userid' not in request.session.keys():
                    return redirect('/live/login')

                # get country id
                articles2FilterData = Articles2.objects.filter(id=event_id).values()
                articles2FilterList = list(articles2FilterData)
                eventCountryName = articles2FilterList[0]['country']
                eventCountryId = AboutCountries.objects.get(country=eventCountryName).table_id
                # ends here ~ get country id

                # filter finance standard charges table
                creditServicesFilter = FinanceStandardCharges.objects.filter(country_id=eventCountryId,service_type=purpose).values('charges_id','fee','fee_type','tax_name','tax_value','service_type','sms','email')
                creditServicesList = list(creditServicesFilter)
                creditServicesDict = creditServicesList[0]
                # ends here ~ filter finance standard charges table

                # formula (for sms): sub_price = fees*(total_credit/sms)
                # formula (for email): sub_price = fees*(total_credit/email)

                return render(request, 'dashboard/add-more-credit.html',{'event_id':event_id,'creditPackageDetails':creditServicesDict, 'credit_type':purpose})
            except Exception as e:
                pass
        ###########################################
    except Exception as e:
        pass
# ends here ~ add more credit

def add_credit_credit_success(request,userid, event_id, charges_id, intialPkgPrice, packageTax, pricePaid, bookingId, purpose_of_payment, organizerEmail,organizerName, invoiceNumberMax, purchaseDate, totalCredits):
    try:
        if purpose_of_payment == 'sms_credit':
            statusPromoFilter = StatusPromotionTicketing.objects.get(event_id=event_id)
            newTotalCredits = statusPromoFilter.sms_credit + totalCredits
            StatusPromotionTicketing.objects.filter(event_id=event_id).update(sms_credit=newTotalCredits)
        elif purpose_of_payment == 'email_credit':
            statusPromoFilter = StatusPromotionTicketing.objects.get(event_id=event_id)
            newTotalCredits = statusPromoFilter.sms_credit + totalCredits
            StatusPromotionTicketing.objects.filter(event_id=event_id).update(email_credit=newTotalCredits)
        return render(request, 'dashboard/package-payment-templates/payment_success_add_more_credit.html',{'total_credit_added':totalCredits, 'purpose_of_payment':purpose_of_payment})

    except Exception as e:
        print(' error in unlock_event_rsvp >> ',e)


# function for content distribution
def content_distribution(request, event_id):
    try:
        eventStatusOnChannelFilter = EventStatusOnChannel.objects.filter(event_id=event_id).values()
        eventStatusOnChannelList = list(eventStatusOnChannelFilter)
        contentDistributionList = []

        articles2FilterData = Articles2.objects.filter(id=event_id).values()
        articles2FilterList = list(articles2FilterData)
        eventName = articles2FilterList[0]['event_name']

        # for loop on EventStatusOnChannel filter data
        for evtStatusChannelData in eventStatusOnChannelList:
            # required variables
            contentDistributionDict = {'site_link':'','site_name':'','promotion_status':'','partner_status':''}
            siteId = evtStatusChannelData['site_id']
            siteLink = evtStatusChannelData['link']
            promotionStatus = evtStatusChannelData['promotion_status']
            partnerStatus = evtStatusChannelData['partner_status']
            # ends here ~ required variables

            # query to get site name and assign to dict key
            partnerSitesFilter = PartnerSites.objects.filter(table_id=siteId).values()
            partnerSitesList = list(partnerSitesFilter)
            if(len(partnerSitesList) > 0):
                contentDistributionDict['site_name'] = partnerSitesList[0]['site_name']
            # ends here ~ query to get site name and assign to dict key

            contentDistributionDict['site_link'] = siteLink
            contentDistributionDict['promotion_status'] = promotionStatus
            contentDistributionDict['partner_status'] = partnerStatus
            contentDistributionList.append(contentDistributionDict.copy())
        # ends here ~ for loop on EventStatusOnChannel filter data

        return render(request, 'dashboard/content-distribution.html',{'content_distribution_list':contentDistributionList, 'event_name':eventName})

    except Exception as e:
        print('error in content_distribution >> ',e)
        # return render(request, 'dashboard/content-distribution.html')

# ends here ~ function for content distribution

# function for create multiple short url
def createMultipleShortUrl(event_id, sourcesPar):
    try:
        sourcesList = sourcesPar

        for source in sourcesList:
            shortUrl = url_shortner.create(event_id,'',source)
    except Exception as e:
        print('error in createMultipleShortUrl function >> ',e)
# ends here ~ function for create multiple short url