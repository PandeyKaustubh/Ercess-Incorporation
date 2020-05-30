from django.shortcuts import render,HttpResponse,redirect,HttpResponseRedirect,reverse,get_object_or_404
# Create your views here.
# from admin_panel.forms import LoginForm,EditForm,AddRsvpForm,AddSalesDetailsForm,AddUserForm
from admin_panel.forms import LoginForm,EditForm,AddRsvpForm,AddSalesDetailsForm, edit_paymentsettlement,EditForm,EditDiscountItemForm
from rest_framework import status
from dashboard.models import Admin,AdminAccesses,AdminActionLog,StatusPromotionTicketing,Articles2,AttendeeFormBuilder,AttendeeFormOptions, AttendeeFormTypes, Tickets,AboutCountries ,TicketsSale,Categories,CategorizedEvents,Topics,EventVerificationResult,EventProcesses,StatusOnChannel,EventStatusOnChannel, PartnerSites,Rsvp,AdminAccessTypes,PaymentSettlement,BankDetails,ErcessIndiaeveStates,ErcessPartnersCategories,DiscountErcess,ErcessPartnersSubcategories,PartnerCurrencies,PartnerTimezones,ErcessOtherMappings, Leads, TicketDiscounts, ReferrerCashbackInfo, ReferrerCashbackTokens,  TicketSalesReference, ErcessOffers, ExpectationsFeedbacks, ShortUrlTracker, CampaignTemplates, CampaignStatus, Leads
from django.core.exceptions import ObjectDoesNotExist
from Ercesscorp.models import Users
from datetime import datetime
from django.contrib import messages
from django.utils import timezone
from django.core.validators import ValidationError
from Ercesscorp.models import UserRegistrationToken
from dashboard.serializers import EditViewSerializer,EditTicketSerializer,TicketDiscountsSerializer
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from django.conf import settings
from django.core.mail import  send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from smtplib import SMTPException
from django.views import View
from django.views.generic import  UpdateView
from django.urls import reverse_lazy
from django.views import generic
from django.core.mail import EmailMultiAlternatives
import hashlib
import string
import random
import json
import csv
import uuid
import time as Time
from datetime import datetime as dt
from django.views.generic import View
import re

def admin_login(request):

    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            email = request.POST.get('email')
            password = request.POST.get('password')
            print(email)

            if Admin.objects.filter(email_id = email).exists():
                print("1st stage")

                if Admin.objects.filter(email_id = email , password = password).exists():
                    print("2nd stage")
                    admin_user = Admin.objects.get(email_id = email)
                    print(admin_user)

                    if admin_user.admin_active == 1:

                        #grabbing sessions from Admin model
                        request.session['admin_id'] = admin_user.table_id
                        request.session['fname'] = admin_user.fname
                        request.session['lname'] = admin_user.lname
                        request.session['mobile'] = admin_user.mobile
                        print(request.session['admin_id'])
                        print(request.session['fname'])

                        access = AdminAccesses.objects.filter(admin_id = admin_user.table_id).order_by('access_type')


                        # grabbing sessions from AdminAccess model
                        print(access)

                        for i in access:
                            type = AdminAccessTypes.objects.all().filter(table_id= i.access_type)
                            request.session['para_'+str(i.access_type)] = type[0].parameter
                            request.session['read_'+str(i.access_type)] = i.read_access
                            request.session['write_'+str(i.access_type)] = i.write_access
                            request.session['delete_'+str(i.access_type)] = i.delete_access
                        print("access is working")

                        for i,j in request.session.items():
                            print(str(i) +" : " +str(j))



                        #storing in access action log
                        access_log = AdminActionLog()
                        access_log.admin_id = request.session['admin_id']
                        access_log.timestamp = datetime.now()
                        access_log.parameter = "log-in"
                        access_log.action_taken = "logged-in"
                        access_log.event_id = 0
                        access_log.save()

                        return redirect('admin-panel:home')
                    else:
                        messages.error(request,"Sorry you dont have admin access")
                else:
                    messages.error(request,'Wrong Password')
            else:
                messages.error(request,'Wrong Admin')
        else:
            messages.error(request,'Form looks invalid')

    return render(request, 'admin_panel/login_admin.html',{'form':form})


def admin_home(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')
    return render(request,'admin_panel/admin_home.html')


def eventList(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    # call getEventProcessList function to fetch all rows from EventProcesses Table
    eventProcessListData = getEventProcessList()
    # ends here ~ call getEventProcessList function to fetch all rows from EventProcesses Table

    new_stat =StatusPromotionTicketing.objects.all().filter(complete_details=1,approval = 0).\
        exclude(event_active =5).order_by('-event_id')

    app_stat =StatusPromotionTicketing.objects.all().filter(complete_details=1,approval=1).\
        exclude(event_active=5).order_by('-event_id')


    unapp_stat =StatusPromotionTicketing.objects.all().filter(complete_details=1,approval=0,event_active=5)

    drafts_stat =StatusPromotionTicketing.objects.all().exclude(complete_details=1)


    time =timezone.now()

    ############################################################---------------------------    UPCOMING TAB
    ###########   NEW EVENT   ###########
    print("NEW EVENT ----------------------------------")
    new_id =[]
    new_name=[]
    new_create =[]
    new_start =[]
    new_username = []
    event_status = []

    for i in new_stat:
        print(i.event_id)
        print(i.connected_user)
        event = Articles2.objects.all().filter(id = i.event_id)
        user =  Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')
        print(user)
        if len(event)!=0:
            if event[0].edate>=time:
                new_id.append(event[0].id)
                new_name.append(event[0].event_name)
                new_create.append(event[0].date_added)
                new_start.append(event[0].sdate)

                if len(user)!=0:
                    new_username.append(user[0].firstname + " " +user[0].lastname)
                else:
                    new_username.append(0)
    print(new_name)
    print(new_username)

    new_items = zip(new_id,new_name,new_create,new_start,new_username,event_status)

    #############   APPROVED EVENTS   ###############
    print("APPROVED     ----------------------------------")
    print(app_stat)
    app_id=[]
    app_name=[]
    app_create=[]
    app_start=[]
    app_user=[]
    event_status = []
    for i in app_stat:
        event = Articles2.objects.all().filter(id = i.event_id)
        user = Users.objects.all().filter(id = i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)

        # print(i.event_status_id,i.event_id,'=========================')
        # event_status_id = i.event_status_id
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        #     # print(status_obj,'=================================================')
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        #     print(event_status,'======================')
        # else:
        #      event_status.append('not available ')
       


        if len(event)!=0:
            if event[0].edate >= time:
                app_id.append(event[0].id)
                app_name.append(event[0].event_name)
                app_create.append(event[0].date_added)
                app_start.append(event[0].sdate)
        
                if len(user)!=0:
                    app_user.append(user[0].firstname + " " + user[0].lastname)
                else:
                    app_user.append(0)
    print(app_name)
    print(app_user)

    app_items = zip(app_id,app_name,app_create,app_start,app_user,event_status)

    ##############    UNAPPROVED EVENTS   ####################
    print("UNAPPROVED              ----------------------------------")
    print(unapp_stat)
    unapp_id=[]
    unapp_name = []
    unapp_create =[]
    unapp_start =[]
    unapp_user = []
    event_status = []
    for i in unapp_stat:

        event = Articles2.objects.all().filter(id = i.event_id)
        user = Users.objects.all().filter(id = i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')

        if len(event)!=0:
            if event[0].edate >= time:
                unapp_id.append(event[0].id)
                unapp_name.append(event[0].event_name)
                unapp_create.append(event[0].date_added)
                unapp_start.append(event[0].sdate)
                

                if len(user)!=0:
                    unapp_user.append(user[0].firstname +" "+user[0].lastname)
                else:
                    unapp_user.append(0)
    print(unapp_name)
    print(unapp_user)

    unapp_items = zip(unapp_id,unapp_name,unapp_create,unapp_start,unapp_user,event_status)

    ###################    DRAFTS    ######################
    print("DRAFTS      ----------------------------------")
    print(drafts_stat)
    d_id =[]
    d_name = []
    d_create = []
    d_start = []
    d_user = []
    event_status = []
    for i in drafts_stat:

        event = Articles2.objects.all().filter(id=i.event_id)
        user = Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')

        if len(event) != 0:
            if event[0].edate >= time:
                d_id.append(event[0].id)
                d_name.append(event[0].event_name)
                d_create.append(event[0].date_added)
                d_start.append(event[0].sdate)
                if len(user) != 0:
                    d_user.append(user[0].firstname + " " + user[0].lastname)
                else:
                    d_user.append(0)
    print(d_name)
    print(d_user)

    draft = zip(d_id,d_name,d_create,d_start,d_user,event_status)

    return render(request,'admin_panel/event_list.html',{'new':new_items,'app':app_items, 'unapp':unapp_items,'draft':draft,'eventProcessesData':eventProcessListData})



def pastEventList(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    app_stat = StatusPromotionTicketing.objects.all().filter(complete_details=1, approval=1). \
        exclude(event_active=5).order_by('-event_id').order_by('-event_id')


    unapp_stat = StatusPromotionTicketing.objects.all().filter(complete_details=1, approval=0, event_active=5).order_by('-event_id')

    drafts_stat = StatusPromotionTicketing.objects.all().exclude(complete_details=1).order_by('-event_id')

    time = timezone.now()

    #############   APPROVED EVENTS   ###############
    print("APPROVED     ----------------------------------")
    # print(app_stat)
    past_app_id = []
    past_app_name = []
    past_app_create = []
    past_app_start = []
    past_app_user = []
    event_status = []
    # past_app_event_status = []

    for i in app_stat:
        event = Articles2.objects.all().filter(id=i.event_id)
        user = Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # print(event_status_id,'=================================================')
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        #     print(status_obj,'====================================')
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')
    
        if len(event) != 0:
            if event[0].edate < time:
                past_app_id.append(event[0].id)
                past_app_name.append(event[0].event_name)
                past_app_create.append(event[0].date_added)
                past_app_start.append(event[0].sdate)

                if len(user) != 0:
                    past_app_user.append(user[0].firstname + " " + user[0].lastname)
                else:
                    past_app_user.append(0)
    # print(past_app_name)
    # print(past_app_user)

    past_app_items = zip(past_app_id, past_app_name, past_app_create, past_app_start, past_app_user,event_status)

    ##############    UNAPPROVED EVENTS   ####################
    print("UNAPPROVED              ----------------------------------")
    print(unapp_stat)
    past_unapp_id = []
    past_unapp_name = []
    past_unapp_create = []
    past_unapp_start = []
    past_unapp_user = []
    event_status = []

    for i in unapp_stat:
        event = Articles2.objects.all().filter(id=i.event_id)
        user = Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')

        if len(event) != 0:
            if event[0].edate < time:
                past_unapp_id.append(event[0].id)
                past_unapp_name.append(event[0].event_name)
                past_unapp_create.append(event[0].date_added)
                past_unapp_start.append(event[0].sdate)
                if len(user) != 0:
                    past_unapp_user.append(user[0].firstname + " " + user[0].lastname)
                else:
                    past_unapp_user.append(0)
    print(past_unapp_name)
    print(past_unapp_user)

    past_unapp_items = zip(past_unapp_id, past_unapp_name, past_unapp_create, past_unapp_start, past_unapp_user,event_status)

    ###################    DRAFTS    ######################
    print("DRAFTS      ----------------------------------")
    print(drafts_stat)
    past_d_id = []
    past_d_name = []
    past_d_create = []
    past_d_start = []
    past_d_user = []
    event_status = []

    for i in drafts_stat:

        event = Articles2.objects.all().filter(id=i.event_id)
        user = Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')

        if len(event) != 0:
            if event[0].edate < time:
                past_d_id.append(event[0].id)

                past_d_name.append(event[0].event_name)
                past_d_create.append(event[0].date_added)
                past_d_start.append(event[0].sdate)
                if len(user) != 0:
                    past_d_user.append(user[0].firstname + " " + user[0].lastname)
                else:
                    past_d_user.append(0)

    past_draft = zip(past_d_id, past_d_name, past_d_create, past_d_start, past_d_user,event_status)

    return render(request,'admin_panel/past_event_list.html',{'past_app':past_app_items,
                                                         'past_unapp':past_unapp_items,'past_draft':past_draft })

def dateRangeEventList(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    app_stat = StatusPromotionTicketing.objects.all().filter(complete_details=1, approval=1). \
        exclude(event_active=5).order_by('-event_id').order_by('-event_id')


    unapp_stat = StatusPromotionTicketing.objects.all().filter(complete_details=1, approval=0, event_active=5).order_by('-event_id')

    drafts_stat = StatusPromotionTicketing.objects.all().exclude(complete_details=1).order_by('-event_id')

    time = timezone.now()

    #############   APPROVED EVENTS   ###############
    print("APPROVED     ----------------------------------")
    # print(app_stat)
    daterange_event_app_id = []
    daterange_event_app_name = []
    daterange_event_app_create = []
    daterange_event_app_start = []
    daterange_event_app_user = []
    event_status = []
    # daterange_event_app_event_status = []

    for i in app_stat:
        event = Articles2.objects.all().filter(id=i.event_id)
        user = Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # print(event_status_id,'=================================================')
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        #     print(status_obj,'====================================')
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')
    
        if len(event) != 0:
            # if event[0].edate < time:
            daterange_event_app_id.append(event[0].id)
            daterange_event_app_name.append(event[0].event_name)
            daterange_event_app_create.append(event[0].date_added)
            daterange_event_app_start.append(event[0].sdate)

            if len(user) != 0:
                daterange_event_app_user.append(user[0].firstname + " " + user[0].lastname)
            else:
                daterange_event_app_user.append(0)
    # print(daterange_event_app_name)
    # print(daterange_event_app_user)

    daterange_event_app_items = zip(daterange_event_app_id, daterange_event_app_name, daterange_event_app_create, daterange_event_app_start, daterange_event_app_user,event_status)

    ##############    UNAPPROVED EVENTS   ####################
    print("UNAPPROVED              ----------------------------------")
    print(unapp_stat)
    daterange_event_unapp_id = []
    daterange_event_unapp_name = []
    daterange_event_unapp_create = []
    daterange_event_unapp_start = []
    daterange_event_unapp_user = []
    event_status = []

    for i in unapp_stat:
        event = Articles2.objects.all().filter(id=i.event_id)
        user = Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')

        if len(event) != 0:
            # if event[0].edate < time:
            daterange_event_unapp_id.append(event[0].id)
            daterange_event_unapp_name.append(event[0].event_name)
            daterange_event_unapp_create.append(event[0].date_added)
            daterange_event_unapp_start.append(event[0].sdate)
            if len(user) != 0:
                daterange_event_unapp_user.append(user[0].firstname + " " + user[0].lastname)
            else:
                daterange_event_unapp_user.append(0)

    daterange_event_unapp_items = zip(daterange_event_unapp_id, daterange_event_unapp_name, daterange_event_unapp_create, daterange_event_unapp_start, daterange_event_unapp_user,event_status)

    ###################    DRAFTS    ######################
    print("DRAFTS      ----------------------------------")
    print(drafts_stat)
    daterange_event_d_id = []
    daterange_event_d_name = []
    daterange_event_d_create = []
    daterange_event_d_start = []
    daterange_event_d_user = []
    event_status = []

    for i in drafts_stat:

        event = Articles2.objects.all().filter(id=i.event_id)
        user = Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')

        if len(event) != 0:
            # if event[0].edate < time:
            daterange_event_d_id.append(event[0].id)

            daterange_event_d_name.append(event[0].event_name)
            daterange_event_d_create.append(event[0].date_added)
            daterange_event_d_start.append(event[0].sdate)
            if len(user) != 0:
                daterange_event_d_user.append(user[0].firstname + " " + user[0].lastname)
            else:
                daterange_event_d_user.append(0)

    daterange_event_draft = zip(daterange_event_d_id, daterange_event_d_name, daterange_event_d_create, daterange_event_d_start, daterange_event_d_user,event_status)
    start_date = end_date = datetime.now().strftime('%m/%d/%Y')
    return render(request,'admin_panel/date_range_event_list.html',{'daterange_event_app':daterange_event_app_items,
                                                         'daterange_event_unapp':daterange_event_unapp_items,'daterange_event_draft':daterange_event_draft,
                                                         'start_date':start_date, 'end_date':end_date })

def createdDateRangeEventList(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')
    
    event_created_daterange = request.POST['event_created_daterange']
    start_date = datetime.strptime(event_created_daterange.split(' - ')[0], '%m/%d/%Y')
    end_date = datetime.strptime(event_created_daterange.split(' - ')[1], '%m/%d/%Y')

    app_stat = StatusPromotionTicketing.objects.all().filter(complete_details=1, approval=1). \
        exclude(event_active=5).order_by('-event_id').order_by('-event_id')


    unapp_stat = StatusPromotionTicketing.objects.all().filter(complete_details=1, approval=0, event_active=5).order_by('-event_id')

    drafts_stat = StatusPromotionTicketing.objects.all().exclude(complete_details=1).order_by('-event_id')

    time = timezone.now()

    #############   APPROVED EVENTS   ###############
    print("APPROVED     ----------------------------------")
    # print(app_stat)
    daterange_event_app_id = []
    daterange_event_app_name = []
    daterange_event_app_create = []
    daterange_event_app_start = []
    daterange_event_app_user = []
    event_status = []
    # daterange_event_app_event_status = []

    for i in app_stat:
        event = Articles2.objects.all().filter(id=i.event_id, date_added__range=(start_date,end_date))
        user = Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # print(event_status_id,'=================================================')
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        #     print(status_obj,'====================================')
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')
    
        if len(event) != 0:
            # if event[0].edate < time:
            daterange_event_app_id.append(event[0].id)
            daterange_event_app_name.append(event[0].event_name)
            daterange_event_app_create.append(event[0].date_added)
            daterange_event_app_start.append(event[0].sdate)

            if len(user) != 0:
                daterange_event_app_user.append(user[0].firstname + " " + user[0].lastname)
            else:
                daterange_event_app_user.append(0)
    # print(daterange_event_app_name)
    # print(daterange_event_app_user)

    daterange_event_app_items = zip(daterange_event_app_id, daterange_event_app_name, daterange_event_app_create, daterange_event_app_start, daterange_event_app_user,event_status)

    ##############    UNAPPROVED EVENTS   ####################
    print("UNAPPROVED              ----------------------------------")
    print(unapp_stat)
    daterange_event_unapp_id = []
    daterange_event_unapp_name = []
    daterange_event_unapp_create = []
    daterange_event_unapp_start = []
    daterange_event_unapp_user = []
    event_status = []

    for i in unapp_stat:
        event = Articles2.objects.all().filter(id=i.event_id, date_added__range=(start_date,end_date))
        user = Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')

        if len(event) != 0:
            # if event[0].edate < time:
            daterange_event_unapp_id.append(event[0].id)
            daterange_event_unapp_name.append(event[0].event_name)
            daterange_event_unapp_create.append(event[0].date_added)
            daterange_event_unapp_start.append(event[0].sdate)
            if len(user) != 0:
                daterange_event_unapp_user.append(user[0].firstname + " " + user[0].lastname)
            else:
                daterange_event_unapp_user.append(0)

    daterange_event_unapp_items = zip(daterange_event_unapp_id, daterange_event_unapp_name, daterange_event_unapp_create, daterange_event_unapp_start, daterange_event_unapp_user,event_status)

    ###################    DRAFTS    ######################
    print("DRAFTS      ----------------------------------")
    print(drafts_stat)
    daterange_event_d_id = []
    daterange_event_d_name = []
    daterange_event_d_create = []
    daterange_event_d_start = []
    daterange_event_d_user = []
    event_status = []

    for i in drafts_stat:

        event = Articles2.objects.all().filter(id=i.event_id, date_added__range=(start_date,end_date))
        user = Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')

        if len(event) != 0:
            # if event[0].edate < time:
            daterange_event_d_id.append(event[0].id)

            daterange_event_d_name.append(event[0].event_name)
            daterange_event_d_create.append(event[0].date_added)
            daterange_event_d_start.append(event[0].sdate)
            if len(user) != 0:
                daterange_event_d_user.append(user[0].firstname + " " + user[0].lastname)
            else:
                daterange_event_d_user.append(0)

    daterange_event_draft = zip(daterange_event_d_id, daterange_event_d_name, daterange_event_d_create, daterange_event_d_start, daterange_event_d_user,event_status)
    start_date = start_date.strftime('%m/%d/%Y')
    end_date = end_date.strftime('%m/%d/%Y')
    return render(request,'admin_panel/date_range_event_list.html',{'daterange_event_app':daterange_event_app_items,
                           'daterange_event_unapp':daterange_event_unapp_items,'daterange_event_draft':daterange_event_draft,
                            'start_date':start_date, 'end_date':end_date, 'search_title': 'Created' })

def startedDateRangeEventList(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    event_started_daterange = request.POST['event_started_daterange']
    start_date = datetime.strptime(event_started_daterange.split(' - ')[0], '%m/%d/%Y')
    end_date = datetime.strptime(event_started_daterange.split(' - ')[1], '%m/%d/%Y')

    app_stat = StatusPromotionTicketing.objects.all().filter(complete_details=1, approval=1). \
        exclude(event_active=5).order_by('-event_id').order_by('-event_id')


    unapp_stat = StatusPromotionTicketing.objects.all().filter(complete_details=1, approval=0, event_active=5).order_by('-event_id')

    drafts_stat = StatusPromotionTicketing.objects.all().exclude(complete_details=1).order_by('-event_id')

    time = timezone.now()

    #############   APPROVED EVENTS   ###############
    print("APPROVED     ----------------------------------")
    # print(app_stat)
    daterange_event_app_id = []
    daterange_event_app_name = []
    daterange_event_app_create = []
    daterange_event_app_start = []
    daterange_event_app_user = []
    event_status = []
    # daterange_event_app_event_status = []

    for i in app_stat:
        event = Articles2.objects.all().filter(id=i.event_id, sdate__range=(start_date,end_date))
        user = Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # print(event_status_id,'=================================================')
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        #     print(status_obj,'====================================')
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')
    
        if len(event) != 0:
            # if event[0].edate < time:
            daterange_event_app_id.append(event[0].id)
            daterange_event_app_name.append(event[0].event_name)
            daterange_event_app_create.append(event[0].date_added)
            daterange_event_app_start.append(event[0].sdate)

            if len(user) != 0:
                daterange_event_app_user.append(user[0].firstname + " " + user[0].lastname)
            else:
                daterange_event_app_user.append(0)
    # print(daterange_event_app_name)
    # print(daterange_event_app_user)

    daterange_event_app_items = zip(daterange_event_app_id, daterange_event_app_name, daterange_event_app_create, daterange_event_app_start, daterange_event_app_user,event_status)

    ##############    UNAPPROVED EVENTS   ####################
    print("UNAPPROVED              ----------------------------------")
    print(unapp_stat)
    daterange_event_unapp_id = []
    daterange_event_unapp_name = []
    daterange_event_unapp_create = []
    daterange_event_unapp_start = []
    daterange_event_unapp_user = []
    event_status = []

    for i in unapp_stat:
        event = Articles2.objects.all().filter(id=i.event_id, sdate__range=(start_date,end_date))
        user = Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')

        if len(event) != 0:
            # if event[0].edate < time:
            daterange_event_unapp_id.append(event[0].id)
            daterange_event_unapp_name.append(event[0].event_name)
            daterange_event_unapp_create.append(event[0].date_added)
            daterange_event_unapp_start.append(event[0].sdate)
            if len(user) != 0:
                daterange_event_unapp_user.append(user[0].firstname + " " + user[0].lastname)
            else:
                daterange_event_unapp_user.append(0)

    daterange_event_unapp_items = zip(daterange_event_unapp_id, daterange_event_unapp_name, daterange_event_unapp_create, daterange_event_unapp_start, daterange_event_unapp_user,event_status)

    ###################    DRAFTS    ######################
    print("DRAFTS      ----------------------------------")
    print(drafts_stat)
    daterange_event_d_id = []
    daterange_event_d_name = []
    daterange_event_d_create = []
    daterange_event_d_start = []
    daterange_event_d_user = []
    event_status = []

    for i in drafts_stat:

        event = Articles2.objects.all().filter(id=i.event_id, sdate__range=(start_date,end_date))
        user = Users.objects.all().filter(id=i.connected_user)
        event_active_id = i.event_active
        event_status.append(event_active_id)
        # event_status_id = i.event_status_id
        # if event_status_id:
        #     status_obj = EventStatus.objects.get(status_id = event_status_id)
        
        #     status_name = status_obj.name
        #     event_status.append(status_name)
        # else:
        #      event_status.append('not available ')

        if len(event) != 0:
            # if event[0].edate < time:
            daterange_event_d_id.append(event[0].id)

            daterange_event_d_name.append(event[0].event_name)
            daterange_event_d_create.append(event[0].date_added)
            daterange_event_d_start.append(event[0].sdate)
            if len(user) != 0:
                daterange_event_d_user.append(user[0].firstname + " " + user[0].lastname)
            else:
                daterange_event_d_user.append(0)

    daterange_event_draft = zip(daterange_event_d_id, daterange_event_d_name, daterange_event_d_create, daterange_event_d_start, daterange_event_d_user,event_status)
    start_date = start_date.strftime('%m/%d/%Y')
    end_date = end_date.strftime('%m/%d/%Y')
    return render(request,'admin_panel/date_range_event_list.html',{'daterange_event_app':daterange_event_app_items,
                        'daterange_event_unapp':daterange_event_unapp_items,'daterange_event_draft':daterange_event_draft,
                        'start_date':start_date, 'end_date':end_date,  'search_title': 'Started'  })

# class EventDetailView(APIView):
#     renderer_classes = [TemplateHTMLRenderer]
#     template_name = 'admin_panel/event_details.html'

#     def get_object(self, event_id):
#         try:
#             return Articles2.objects.get(pk=event_id)
#         except Articles2.DoesNotExist:
#             raise Http404

#     def get(self, request,event_id):
#         if 'admin_id' not in request.session.keys():
#             return redirect('/admin-site/login')

#         form = EditForm()
#         # call getEventProcessList function to fetch all rows from EventProcesses Table
#         eventProcessListData = getEventProcessList()
#         # ends here ~ call getEventProcessList function to fetch all rows from EventProcesses Table


#         id = event_id
#         article = self.get_object(event_id)
#         serializer = EditViewSerializer(article)
#         country=article.country
#         pro_image= article.profile_image
#         banner = article.banner
#         edit_image = article.editable_image
#         website = article.website
#         ticket_url = article.ticket_url

#         images = [pro_image,banner,edit_image]

#         #Target Tab----------------------------------------------------------
#         s_p_tkt = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
#         print(s_p_tkt)
#         types=''
#         tkt_typ=''
#         for i in s_p_tkt:
#             types = i.private
#             tkt_typ = i.ticketing
#         print(types)
#         if types == 0 :
#             types = 'public'
#         else:
#             types = 'private'

#         if tkt_typ == 0:
#             tkt_typ = 'free'
#         else:
#             tkt_typ = 'paid'
#         print(types)
#         print(tkt_typ)

#         cat_event = CategorizedEvents.objects.all().filter(event_id = event_id)
#         print(cat_event)
#         cat_id = cat_event[0].category_id
#         top_id = cat_event[0].topic_id

#         topic = Topics.objects.all().filter(topics_id = top_id)
#         category = Categories.objects.all().filter(category_id = cat_id)

#         main_category = category[0].category
#         print(main_category)
#         sub_category=''
#         if len(topic)!=0:
#             sub_category = topic[0].topic
#         elif len(topic)==0:
#             sub_category = " "
#         print(sub_category)
#         cat = (main_category,sub_category)

#         #Tickets Tab--------------------------------------------------------
#         free =False
#         if s_p_tkt[0].ticketing == 0:
#             free = True

#         tkts = Tickets.objects.all().filter(event_id = event_id)
#         print(tkts)
#         tkt_name = []
#         tkt_price = []
#         oth_chrgs = []
#         oth_chrgs_type =[]
#         tkt_qty = []
#         min_qty = []
#         max_qty = []
#         tkt_left = []
#         tkt_msg = []
#         s_date = []
#         e_date = []
#         e_fee = []
#         trans_fee = []
#         tkt_lbl = []
#         activ = []

#         for i in tkts:
#             tkt_name.append(i.ticket_name)
#             tkt_price.append(i.ticket_price)
#             oth_chrgs.append(i.other_charges)
#             oth_chrgs_type.append(i.other_charges_type)
#             tkt_qty.append(i.ticket_qty)
#             min_qty.append(i.min_qty)
#             max_qty.append(i.max_qty)
#             tkt_left.append(i.qty_left)
#             tkt_msg.append(i.ticket_msg)
#             s_date.append(i.ticket_start_date)
#             e_date.append(i.expiry_date)
#             e_fee.append(i.ercess_fee)
#             trans_fee.append(i.transaction_fee)
#             tkt_lbl.append(i.ticket_label)
#             activ.append(i.active)
#         print(oth_chrgs)
#         print("message-------------")
#         print(tkt_msg)
#         msg1=[]
#         for i in tkt_msg:
#             if (i == None or i == "" or i =="None" or i == "NULL" or i == "none"):
#                 msg1.append(0)
#             else:
#                 msg1.append(i)
#         print(msg1)
#         print("message code------------------ends")
#         oth_chrgs2=[]
#         for i in oth_chrgs:
#             if i == '':
#                 oth_chrgs2.append(0)
#             else:
#                 oth_chrgs2.append(i)
#         print(oth_chrgs2)

#         print(oth_chrgs_type)
#         oth_chrgs_type2=[]
#         for i in oth_chrgs_type:
#             if i == 0:
#                 oth_chrgs_type2.append(0)
#             elif i == 1:
#                 oth_chrgs_type2.append(1)
#             elif i == 2 :
#                 oth_chrgs_type2.append(2)
#         print(oth_chrgs_type2)

#         print(activ)
#         activ2=[]
#         for i in activ:
#             if i == 0:
#                 activ2.append('inactive')
#             elif i == 1:
#                 activ2.append('active')
#             elif i == 2:
#                 activ2.append("deleted")
#         print(activ2)
#         print(country)

#         currency = AboutCountries.objects.all().filter(country= country).values('currency')

#         # @author Shubham ~ october 10 2019
#         if not currency:
#             currency = ''
#         else:
#             currency = currency[0]['currency']
#         # ends here ~ @author Shubham ~ october 10 2019


#         print("Question tab---------------------------")
#         # Question Tab
#         builder = AttendeeFormBuilder.objects.all().filter(event_id=event_id)
#         print(builder)
#         title = []
#         mand = []
#         q_type = []
#         q_id = []
#         if len(builder) != 0:
#             for i in builder:
#                 title.append(i.ques_title)
#                 mand.append(i.ques_accessibility)
#                 q_type.append(i.ques_type)
#                 q_id.append(i.ques_id)
#         print(title)

#         print(mand)

#         name = []
#         type_id = []
#         for i in q_type:
#             form_type = AttendeeFormTypes.objects.all().filter(type_id=i)
#             name.append(form_type[0].name)
#             type_id.append(form_type[0].type_id)
#         print(name)

#         optn_name = []
#         for i in q_id:
#             form_option = AttendeeFormOptions.objects.all().filter(ques_id=i)
#             if len(form_option) != 0:
#                 if form_option[0].event_id == event_id:
#                     optn_name.append(form_option[0].option_name)
#                 else:
#                     optn_name.append(" ")
#             else:
#                 optn_name.append(" ")
#         print(optn_name)

#         x = zip(title, mand, name, optn_name)

#         items = zip(tkt_name, tkt_price, oth_chrgs2,
#                     oth_chrgs_type2, tkt_qty, min_qty,
#                     max_qty, tkt_left, msg1, s_date, e_date,
#                     e_fee, trans_fee, tkt_lbl, activ2)

#         #################     for fail errors   #####################
#         print("Fail errors---------------------------")
#         veri_res = EventVerificationResult.objects.all().filter(event_id=event_id)
#         print(veri_res.values('event_id'))
#         veri_id = []
#         pass_id =[]
#         if len(veri_res) != 0:
#             for i in veri_res:
#                 if i.status == 'fail':
#                     veri_id.append(i.verified_against)
#                     # veri_id = eval(i.verified_against)
#                 elif i.status == 'pass':
#                     pass_id.append(i.verified_against)
#                     # pass_id = eval(i.verified_against)
#         veri_count = len(veri_id)
#         pass_count = len(pass_id)
        
     

#         print(veri_id)
#         print(pass_id)
#         msg_to_org = []

#         for i in veri_id: #old code
#         # for i in list(veri_id): #new code
#             process = EventProcesses.objects.all().filter(process_id=i)
#             msg_to_org.append(process[0].msg_to_org)
#         msg_to_org_pass =[]
#         for i in pass_id:
#             process= EventProcesses.objects.all().filter(process_id=i)
#             msg_to_org_pass.append(process[0].msg_to_org)
#         print(msg_to_org)
#         print("-------------------------fail errors")

#         ###################################### for sales box    ##################################
#         sales = TicketsSale.objects.all().filter(event_id=event_id)
#         print(sales)
#         t_count = len(sales)
#         print(t_count)

#         tkt_type = []
#         tkt_qty = []
#         tkt_amt = []
#         tkt_p_date = []
#         tkt_s_site = []
#         tkt_atendee = []
#         tkt_book_id = []
#         contact = []
#         email = []
#         recieve = []
#         forward = []
#         tableId = []

#         if t_count != 0:
#             for i in sales:
#                 print(i)
#                 tkt_book_id.append(i.booking_id)
#                 tkt_type.append(i.ticket_type)
#                 tkt_amt.append(i.ampunt_paid)
#                 tkt_qty.append(i.qty)
#                 tkt_p_date.append(i.purchase_date)
#                 tkt_s_site.append(i.seller_site)
#                 tkt_atendee.append(i.attendee_name)
#                 contact.append(i.attendee_contact)
#                 email.append(i.attendee_email)
#                 tableId.append(i.table_id)



#         details = zip(tkt_type, tkt_book_id, tkt_amt, tkt_qty, tkt_p_date, tkt_s_site, tkt_atendee,contact
#                       ,email,tableId)

#         ##########################  RSVP  BOX    ############################################

#         name_r = []
#         cont = []
#         email = []
#         locked_status = []
#         e_r = Rsvp.objects.all().filter(event_id=event_id).order_by('-date_added').values('table_id')

#         # @author Shubham ~ filter rsvp objects using event_id
#         # for i in range(0, len(e_r)):
#         #     d = Rsvp.objects.all().filter(table_id=e_r[i]['table_id'])
#         #     name_r.append(d.values('attendee_name')[0]['attendee_name'])
#         #     cont.append(d.values('attendee_contact')[0]['attendee_contact'])
#         #     email.append(d.values('attendee_email')[0]['attendee_email'])

#         print('----------------------->>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<--------------------------')
#         # filterRsvpData = Rsvp.objects.filter(event_id=event_id)
#         filterRsvpListData = e_r.values()
#         rsvp_list_data = [entry for entry in filterRsvpListData]
#         for rsvp_data in rsvp_list_data:
#             name_r.append(rsvp_data['attendee_name'])
#             cont.append(rsvp_data['attendee_contact'])
#             email.append(rsvp_data['attendee_email'])
#             locked_status.append(rsvp_data['locked'])


#         print('----------------------->>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<--------------------------')
#         print(event_id)

#         rsvp_d = zip(name_r, cont, email, locked_status)
#         c_r = [len(e_r)]

#         # ends here ~ @author Shubham ~ filter rsvp objects using event_id

#     #######################################     SITE   TABLE   ######################################

#         s_n = []
#         c_l = []
#         c_ps = []
#         c_p = []

#         s = EventStatusOnChannel.objects.all().filter(event_id=event_id).values('table_id')
#         s_len = len(s)
#         print(s)
#         for i in s:
#             d = EventStatusOnChannel.objects.all().filter(table_id=i['table_id'])
#             s_i = PartnerSites.objects.all().filter(table_id=(d.values('site_id')[0]['site_id']))
#             s_n.append(s_i.values('site_name')[0]['site_name'])
#             c_l.append(d.values('link')[0]['link'])
#             c_ps.append(d.values('promotion_status')[0]['promotion_status'])
#             c_p.append(d.values('partner_status')[0]['partner_status'])

#         print(c_l)

#         print("Link ----------------------------------")
#         print(c_l)
#         site_link = []
#         for i in c_l:
#             if (i == None or i == '' or i == "None" or i == "none" or i == "NULL"):
#                 site_link.append(0)
#             else:
#                 site_link.append(i)
#         print(site_link)

#         print("----------------------------------ends link")
#         site = zip(s_n, site_link, c_ps, c_p)


#         ''' Status promotion ticket table , fetching approval of event '''

#         status = StatusPromotionTicketing.objects.get(event_id = event_id)


#         # @author shubham ~ fetch sites from PartnerSites Table
#         filterSiteData = PartnerSites.objects.all().values('site_name').order_by('site_name')
#         siteNameList = list(filterSiteData)
#         # ends here ~ @author shubham ~ fetch sites from PartnerSites Table

#         # get current user bank details
#         bankDetailsInfo = getBankDetails(event_id)
#         userDetailsInfo = getOrganiserDetails(event_id)
#         # ends here ~ get current login user bank details

#         # get referrer cashback info data
#         referrerCashbackFilter = ReferrerCashbackInfo.objects.all().exclude(ticket_sales_id=None)
#         referrerCashbackList = list(referrerCashbackFilter
#             )
#         # ends here ~ get referrer cashback info data


#         return Response({'id':id,'form':form,'article': article,'cat':cat,'images':images,'detail':details,'rsvp':rsvp_d,
#                          'c_r':c_r,'site':site,'s_len':s_len,'website':website,
#                          'types':types ,'currency':currency,'free':free,
#                          'tkt_typ':tkt_typ,'items':items,'x':x,'fail':msg_to_org,'pass':msg_to_org_pass, 'status':status, 'siteNameList':siteNameList,'bankDetailsInfo':bankDetailsInfo,'eventProcessesData':eventProcessListData, 'referrerCashbackData':referrerCashbackList, 'userDetailsInfo':userDetailsInfo})

#     def post(self,request ,event_id):
#         if 'admin_id' not in request.session.keys():
#             return redirect('/admin-site/login')
#         time = timezone.now()
#         status = False
#         if request.method == 'POST':
#             form = EditForm(request.POST)
#             if form.is_valid():
#                 name = request.POST.get('website_name')
#                 link = request.POST.get('link')
#                 prom = request.POST.get('promotion_status')
#                 part = request.POST.get('partner_status')

#                 print(name)
#                 print(prom)
#                 print(part)

#                 eve_channel = EventStatusOnChannel.objects.all().filter(event_id=event_id, site_id=name)
#                 if len(eve_channel) != 0:
#                     ############################  UPDATING THE ROW   ######################################

#                     print(eve_channel)
#                     print(eve_channel[0].promotion_status)
#                     print(eve_channel[0].partner_status)
#                     eve_channel[0].promotion_status = prom
#                     eve_channel[0].partner_status = part
#                     eve_channel[0].link = link
#                     eve_channel[0].last_updated = time
#                     print("new----------")
#                     print(eve_channel[0].promotion_status)
#                     print(eve_channel[0].partner_status)
#                     eve_channel[0].save()
#                     status = True
#                 else:
#                     ################################     NEW ROW CREATING    ##################################

#                     eve_c = EventStatusOnChannel()
#                     eve_c.event_id = event_id
#                     eve_c.last_updated = time
#                     eve_c.site_id = name
#                     eve_c.admin_id = request.session['admin_id']
#                     eve_c.link = link
#                     eve_c.promotion_status = prom
#                     eve_c.partner_status = part
#                     eve_c.save()
#                     status = True

#                 #########################  SAVING ADMIN ACTION LOG   ########################################

#                 action = AdminActionLog()
#                 action.admin_id = request.session['admin_id']
#                 action.timestamp = time
#                 action.parameter = "promotion link"
#                 action.event_id = event_id
#                 p = PartnerSites.objects.get(table_id=name)
#                 print(p)
#                 action.action_taken = "updated the details of " + p.site_name
#                 action.save()

#                 return redirect('admin-panel:details',event_id=event_id)
#             else:
#                 status=False
#                 messages.error(request,"Something went wrong")

##############ENDS HERE ~ OLD WORKING FUNCTION#############

###################################################
######### OLD FUNCTION with Modifications #########
###################################################


class EventDetailView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'admin_panel/event_details.html'

    def get_object(self, event_id):
        try:
            return Articles2.objects.get(pk=event_id)
        except Articles2.DoesNotExist:
            raise Http404

    def get_discount_item(self,table_id):
        try:
            return TicketDiscounts.objects.get(pk=table_id)
        except TicketDiscounts.DoesNotExist:
            return Http404

    def get(self, request,event_id):
        if 'admin_id' not in request.session.keys():
            return redirect('/admin-site/login')

        form = EditForm()
        # call getEventProcessList function to fetch all rows from EventProcesses Table
        eventProcessListData = getEventProcessList()
        # ends here ~ call getEventProcessList function to fetch all rows from EventProcesses Table


        id = event_id
        # event_status = EventStatus.objects.all()

        short_url = ShortUrlTracker.objects.filter(event_id=event_id)
        article = self.get_object(event_id)
        serializer = EditViewSerializer(article)
        country=article.country
        pro_image= article.profile_image
        banner = article.banner
        edit_image = article.editable_image
        website = article.website
        ticket_url = article.ticket_url

        images = [pro_image,banner,edit_image]

        #Target Tab----------------------------------------------------------
        s_p_tkt = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
       
        # s_p_tkt.event_status_id
        types=''
        tkt_typ=''
        affiliate = 0
        sms_credit = 0
        email_credit = 0
        for i in s_p_tkt:
            types = i.private
            tkt_typ = i.ticketing
            event_status_id = i.event_active
            affiliate = i.affiliate
            sms_credit = i.sms_credit
            email_credit = i.email_credit
        print(types)
        if types == 0 :
            types = 'public'
        else:
            types = 'private'

        if tkt_typ == 0:
            tkt_typ = 'free'
        else:
            tkt_typ = 'paid'
        print(types)
        print(tkt_typ)

        cat_event = CategorizedEvents.objects.all().filter(event_id = event_id)
        print(cat_event)

        # @author Shubham ~ Code Modify ~ December 10 2019 (out of index error)
        if(len(cat_event) > 0):
            cat_id = cat_event[0].category_id
            top_id = cat_event[0].topic_id
        else:
            cat_id = 0
            top_id = 0
        # ends here ~ @author Shubham ~ Code Modify ~ December 10 2019 (out of index error)

        topic = Topics.objects.all().filter(topics_id = top_id)
        category = Categories.objects.all().filter(category_id = cat_id)

        # @author Shubham ~ Code Modify ~ December 10 2019 (out of index error)
        if(len(category) > 0):
            main_category = category[0].category
        else:
            main_category = 0
        # ends here ~ @author Shubham ~ Code Modify ~ December 10 2019 (out of index error)
        print(main_category)
        sub_category=''
        if len(topic)!=0:
            sub_category = topic[0].topic
        elif len(topic)==0:
            sub_category = " "
        print(sub_category)
        cat = (main_category,sub_category)

        #Tickets Tab--------------------------------------------------------
        free =False
        # @author Shubham ~ Code Modify ~ December 10 2019 (out of index error)
        if(len(s_p_tkt) > 0):
            if s_p_tkt[0].ticketing == 0:
                free = True
        # ends here ~ @author Shubham ~ Code Modify ~ December 10 2019 (out of index error)

        tkts = Tickets.objects.all().filter(event_id = event_id)
        print(tkts)
        tkt_name = []
        tkt_price = []
        oth_chrgs = []
        oth_chrgs_type =[]
        tkt_qty = []
        min_qty = []
        max_qty = []
        tkt_left = []
        tkt_msg = []
        s_date = []
        e_date = []
        e_fee = []
        trans_fee = []
        tkt_lbl = []
        activ = []

        for i in tkts:
            tkt_name.append(i.ticket_name)
            tkt_price.append(i.ticket_price)
            oth_chrgs.append(i.other_charges)
            oth_chrgs_type.append(i.other_charges_type)
            tkt_qty.append(i.ticket_qty)
            min_qty.append(i.min_qty)
            max_qty.append(i.max_qty)
            tkt_left.append(i.qty_left)
            tkt_msg.append(i.ticket_msg)
            s_date.append(i.ticket_start_date)
            e_date.append(i.expiry_date)
            e_fee.append(i.ercess_fee)
            trans_fee.append(i.transaction_fee)
            tkt_lbl.append(i.ticket_label)
            activ.append(i.active)
        print(oth_chrgs)
        print("message-------------")
        print(tkt_msg)
        msg1=[]
        for i in tkt_msg:
            if (i == None or i == "" or i =="None" or i == "NULL" or i == "none"):
                msg1.append(0)
            else:
                msg1.append(i)
        print(msg1)
        print("message code------------------ends")
        oth_chrgs2=[]
        for i in oth_chrgs:
            if i == '':
                oth_chrgs2.append(0)
            else:
                oth_chrgs2.append(i)
        print(oth_chrgs2)

        print(oth_chrgs_type)
        oth_chrgs_type2=[]
        for i in oth_chrgs_type:
            if i == 0:
                oth_chrgs_type2.append(0)
            elif i == 1:
                oth_chrgs_type2.append(1)
            elif i == 2 :
                oth_chrgs_type2.append(2)
        print(oth_chrgs_type2)

        print(activ)
        activ2=[]
        for i in activ:
            if i == 0:
                activ2.append('inactive')
            elif i == 1:
                activ2.append('active')
            elif i == 2:
                activ2.append("deleted")
        print(activ2)
        print(country)

        currency = AboutCountries.objects.all().filter(country= country).values('currency')

        # @author Shubham ~ october 10 2019
        if not currency:
            currency = ''
        else:
            # @author Shubham ~ Code Modify ~ December 10 2019 (out of index error)
            if(len(currency)>0):
                if ('currency' in currency[0]):
                    currency = currency[0]['currency']
                else:
                    currency = ''    
            else:
                currency = ''
            # ends here ~ @author Shubham ~ Code Modify ~ December 10 2019 (out of index error)
        # ends here ~ @author Shubham ~ october 10 2019


        print("Question tab---------------------------")
        # Question Tab
        builder = AttendeeFormBuilder.objects.all().filter(event_id=event_id)
        print(builder)
        title = []
        mand = []
        q_type = []
        q_id = []
        if len(builder) != 0:
            for i in builder:
                title.append(i.ques_title)
                mand.append(i.ques_accessibility)
                q_type.append(i.ques_type)
                q_id.append(i.ques_id)
        print(title)

        print(mand)

        name = []
        type_id = []
        for i in q_type:
            form_type = AttendeeFormTypes.objects.all().filter(type_id=i)
            name.append(form_type[0].name)
            type_id.append(form_type[0].type_id)
        print(name)

        optn_name = []
        for i in q_id:
            form_option = AttendeeFormOptions.objects.all().filter(ques_id=i)
            if len(form_option) != 0:
                if form_option[0].event_id == event_id:
                    optn_name.append(form_option[0].option_name)
                else:
                    optn_name.append(" ")
            else:
                optn_name.append(" ")
        print(optn_name)

        x = zip(title, mand, name, optn_name)

        items = zip(tkt_name, tkt_price, oth_chrgs2,
                    oth_chrgs_type2, tkt_qty, min_qty,
                    max_qty, tkt_left, msg1, s_date, e_date,
                    e_fee, trans_fee, tkt_lbl, activ2)

        #################     for fail errors   #####################
        print("Fail errors---------------------------")
        veri_res = EventVerificationResult.objects.all().filter(event_id=event_id)
        print(veri_res.values('event_id'))
        veri_id = []
        pass_id =[]
        if len(veri_res) != 0:
            for i in veri_res:
                if i.status == 'fail':
                    veri_id.append(i.verified_against)
                    # veri_id = eval(i.verified_against)
                elif i.status == 'pass':
                    pass_id.append(i.verified_against)
                    # pass_id = eval(i.verified_against)
        veri_count = len(veri_id)
        pass_count = len(pass_id)
        
     

        print(veri_id)
        print(pass_id)
        msg_to_org = []

        for i in veri_id: #old code
        # for i in list(veri_id): #new code
            process = EventProcesses.objects.all().filter(process_id=i)
            msg_to_org.append(process[0].msg_to_org)
        msg_to_org_pass =[]
        for i in pass_id:
            process= EventProcesses.objects.all().filter(process_id=i)
            msg_to_org_pass.append(process[0].msg_to_org)
        print(msg_to_org)
        print("-------------------------fail errors")

        ###################################### for sales box    ##################################
        sales = TicketsSale.objects.all().filter(event_id=event_id)
        print(sales)
        t_count = len(sales)
        print(t_count)

        tkt_type = []
        tkt_qty = []
        tkt_amt = []
        tkt_p_date = []
        tkt_s_site = []
        tkt_atendee = []
        tkt_book_id = []
        contact = []
        email = []
        recieve = []
        forward = []
        tableId = []

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
                contact.append(i.attendee_contact)
                email.append(i.attendee_email)
                tableId.append(i.table_id)



        details = zip(tkt_type, tkt_book_id, tkt_amt, tkt_qty, tkt_p_date, tkt_s_site, tkt_atendee,contact
                      ,email,tableId)

        ##########################  RSVP  BOX    ############################################

        name_r = []
        cont = []
        email = []
        locked_status = []
        e_r = Rsvp.objects.all().filter(event_id=event_id).order_by('-date_added').values('table_id')

        # @author Shubham ~ filter rsvp objects using event_id
        # for i in range(0, len(e_r)):
        #     d = Rsvp.objects.all().filter(table_id=e_r[i]['table_id'])
        #     name_r.append(d.values('attendee_name')[0]['attendee_name'])
        #     cont.append(d.values('attendee_contact')[0]['attendee_contact'])
        #     email.append(d.values('attendee_email')[0]['attendee_email'])

        print('----------------------->>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<--------------------------')
        # filterRsvpData = Rsvp.objects.filter(event_id=event_id)
        filterRsvpListData = e_r.values()
        rsvp_list_data = [entry for entry in filterRsvpListData]
        for rsvp_data in rsvp_list_data:
            name_r.append(rsvp_data['attendee_name'])
            cont.append(rsvp_data['attendee_contact'])
            email.append(rsvp_data['attendee_email'])
            locked_status.append(rsvp_data['locked'])


        print('----------------------->>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<--------------------------')
        print(event_id)

        rsvp_d = zip(name_r, cont, email, locked_status)
        c_r = [len(e_r)]

        # ends here ~ @author Shubham ~ filter rsvp objects using event_id

    #######################################     SITE   TABLE   ######################################

        s_n = []
        c_l = []
        c_ps = []
        c_p = []

        s = EventStatusOnChannel.objects.all().filter(event_id=event_id).values('table_id')
        s_len = len(s)
        print(s)
        for i in s:
            d = EventStatusOnChannel.objects.all().filter(table_id=i['table_id'])
            s_i = PartnerSites.objects.all().filter(table_id=(d.values('site_id')[0]['site_id']))
            s_n.append(s_i.values('site_name')[0]['site_name'])
            c_l.append(d.values('link')[0]['link'])
            c_ps.append(d.values('promotion_status')[0]['promotion_status'])
            c_p.append(d.values('partner_status')[0]['partner_status'])

        print(c_l)

        print("Link ----------------------------------")
        print(c_l)
        site_link = []
        for i in c_l:
            if (i == None or i == '' or i == "None" or i == "none" or i == "NULL"):
                site_link.append(0)
            else:
                site_link.append(i)
        print(site_link)

        print("----------------------------------ends link")
        site = zip(s_n, site_link, c_ps, c_p)


        ''' Status promotion ticket table , fetching approval of event '''

        status = StatusPromotionTicketing.objects.get(event_id = event_id)


        # @author shubham ~ fetch sites from PartnerSites Table
        filterSiteData = PartnerSites.objects.all().values('site_name').order_by('site_name')
        siteNameList = list(filterSiteData)
        # ends here ~ @author shubham ~ fetch sites from PartnerSites Table

        # get current user bank details
        bankDetailsInfo = getBankDetails(event_id)
        userDetailsInfo = getOrganiserDetails(event_id)
        # ends here ~ get current login user bank details

        # get referrer cashback info data
        referrerCashbackFilter = ReferrerCashbackInfo.objects.all()
        referrerCashbackList = list(referrerCashbackFilter
            )
        # ends here ~ get referrer cashback info data

        # @author Shubham ~ Get custom question from db to display on UI ~ december 10 2019
        builder_list_final = []
        try:
            builder = AttendeeFormBuilder.objects.filter(event_id=event_id).values()
            builderListVal = list(builder)

            qs_types = AttendeeFormTypes.objects.values_list('type_id', 'name')
            qs_types_new = AttendeeFormTypes.objects.all().values()
            

            for builder_list in builderListVal:
                customQuestionDict = {'ques_title': '', 'ques_type': '', 'ques_accessibility':'', 'option_name':''}
                customQuestionDict['ques_title'] = builder_list['ques_title']
                
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

                customQuestionDict['ques_type'] = AttendeeFormTypes.objects.get(type_id=builder_list['ques_type']).name
                

                builder_list_final.append(customQuestionDict.copy())
        except:
            pass

        # ends here ~ @author Shubham ~ Get custom question from db to display on UI ~ december 10 2019
        ### - Adding discount tab  @Ajitesh #####
        discount_event_list = TicketDiscounts.objects.filter(event_id=event_id)
        discount_response_list=[]
        for discounts in discount_event_list:
            ticket = Tickets.objects.get(tickets_id=discounts.ticket_id)
            get_ticket_name = ticket.ticket_name
            response = {'table_id':discounts.table_id,'event_id':discounts.event_id,'tickets':get_ticket_name,'coupon':discounts.coupon,'amount':discounts.discount_amt,
                        'type':discounts.discount_type,'start': discounts.discount_start,'end':discounts.discount_end,'active':discounts.active}
            discount_response_list.append(response)
        print(discount_response_list)
        print('\n\n\n\n\n\n')
        print('===========-------------------=======================')
        print('short_url : ',short_url)
        return Response({'id':id,'form':form,'article': article,'cat':cat,'images':images,'detail':details,'rsvp':rsvp_d,
                         'c_r':c_r,'site':site,'s_len':s_len,'website':website,'types':types,'currency':currency,
                         'free':free,'tkt_typ':tkt_typ,'affiliate':affiliate,'sms_credit':sms_credit,'email_credit':email_credit,
                         'items':items,'x':x,'fail':msg_to_org,'pass':msg_to_org_pass, 'status':status, 'siteNameList':siteNameList,
                         'bankDetailsInfo':bankDetailsInfo,'eventProcessesData':eventProcessListData, 'referrerCashbackData':referrerCashbackList,
                         'userDetailsInfo':userDetailsInfo, 'custom_question_list':builder_list_final, 's_p_tkt':s_p_tkt, 'short_url':short_url,'discounts':discount_response_list})

    
    def post(self,request,event_id,ticket_id):
        
        form = EditDiscountItemForm(request.POST)
        print(form)
        print('###########################################- XXXX ----################################################')
        table_id = request.POST.get('table_id')
        ticket_name =request.POST.get('ticket_name')
        print('########################################### - XXXXX -----################################################')
        get_discount_item = self.get_discount_item(table_id)
        get_ticket = Tickets.objects.get(ticket_name=ticket_name,event_id=event_id)
        print('Start = ',request.POST.get('start-date'),request.POST.get('end-date'))
        data = {
            'table_id' : request.POST.get('table_id'),
            'ticket_name' : get_ticket.tickets_id,
            'discount_amt' : request.POST.get('amount'),
            'discount_type' :  request.POST.get('type'),
            'active' : request.POST.get('active')
        }
        serializer = TicketDiscountsSerializer(get_discount_item,data=data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return redirect('admin-panel:details',event_id=event_id)
        print(serializer.errors)

        return redirect('admin-panel:details',event_id=event_id)
###################################################
### ENDS HERE ~ OLD FUNCTION with Modifications ###
###################################################
def promotionUpcoming(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    app_stat = StatusPromotionTicketing.objects.all().order_by('-event_id')

    time = timezone.now()
        #############   ALL EVENTS   ###############
    print("ALL    ----------------------------------")
    print(app_stat)
    app_id = []

    for i in app_stat:
        event = Articles2.objects.all().filter(id=i.event_id)


        if len(event) != 0:
            if event[0].edate >= time:
                app_id.append(event[0].id)
    print(app_id)

    eve_id =[]
    eve_name = []
    site_name = []
    link = []
    prom_stat = []
    partner = []

    for i in app_id:
        status = EventStatusOnChannel.objects.all().filter(event_id=i)

        for i in status:
            event2= Articles2.objects.all().filter(id = i.event_id)
            site = PartnerSites.objects.all().filter(table_id=i.site_id)
            if len(event2)!=0:
                eve_id.append(i.event_id)
                eve_name.append(event2[0].event_name)
                site_name.append(site[0].site_name)
                link.append(i.link)
                prom_stat.append(i.promotion_status)
                partner.append(i.partner_status)
    print(eve_id)
    print(eve_name)
    print(len(eve_id),len(eve_name), len(site_name), len(link), len(prom_stat), len(partner))

    up =zip(eve_id,eve_name,site_name,link,prom_stat,partner)
    return render(request,'admin_panel/prom_upcoming.html',{'up':up})


def promotionPast(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')
    app_stat = StatusPromotionTicketing.objects.all().order_by('-event_id')

    print(request.session['fname'])

    time = timezone.now()

    #############   ALL EVENTS   ###############
    print("ALL    ----------------------------------")
    print(app_stat)
    app_id = []

    for i in app_stat:
        event = Articles2.objects.all().filter(id=i.event_id)

        if len(event) != 0:
            if event[0].edate < time:
                app_id.append(event[0].id)
    print(app_id)

    eve_id = []
    eve_name = []
    site_name = []
    link = []
    prom_stat = []
    partner = []

    for i in app_id:
        status = EventStatusOnChannel.objects.all().filter(event_id=i)

        for i in status:
            event2 = Articles2.objects.all().filter(id=i.event_id)
            site = PartnerSites.objects.all().filter(table_id=i.site_id)
            if len(event2) != 0:
                eve_id.append(i.event_id)
                eve_name.append(event2[0].event_name)
                site_name.append(site[0].site_name)
                link.append(i.link)
                prom_stat.append(i.promotion_status)
                partner.append(i.partner_status)
    print(eve_id)
    print(eve_name)
    print(len(eve_id), len(eve_name), len(site_name), len(link), len(prom_stat), len(partner))

    past = zip(eve_id, eve_name, site_name, link, prom_stat, partner)

    return render(request,'admin_panel/prom_past.html',{'past':past})


def partner_sites(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    all = PartnerSites.objects.all()

    partners_site = []
    for i in all:
        partners_site.append(i)

    acount = 0
    dcount = 0
    for i in partners_site:
        if i.active_state == 1:
            acount+=1
        else:
            dcount +=1

    return render(request, 'admin_panel/partnersites.html', {'partners_site':partners_site, 'acount':acount, 'dcount':dcount} )

def user_detail(request):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    users = Users.objects.all()

    # user= []

    # for i in users:
    #     user.append(i)
    # no_of_user = len(user)

    return render(request, 'admin_panel/users_detail.html', {'users': users, 'no_of_user':users.count()})

def display_user_event(request, user_id):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    data_list=[]
    try:
        spt = StatusPromotionTicketing.objects.values_list('event_id',flat=True).filter(connected_user=user_id).order_by('-connected_user')

        all_arti = Articles2.objects.order_by('-sdate').filter(id__in = spt)

        for i in all_arti:
            resp={}
            resp['id'] = i.id
            resp['event_name'] = i.event_name
            resp['sdate'] = i.sdate
            resp['edate'] = i.edate
            data_list.append(resp)

    except Exception as e:
        pass

    return render(request, 'admin_panel/display_user_event.html', {'event': data_list, 'no_of_event':len(data_list)})


# def add_rsvp(request, event_id):
#     if 'admin_id' not in request.session.keys():
#         return redirect('/admin-site/login')

#     if request.method == 'POST':
#         form = AddRsvpForm(request.POST)
#         if form.is_valid():
#             sitename = form.cleaned_data['sitename']
#             name = form.cleaned_data['name']
#             email = form.cleaned_data['email']
#             number = form.cleaned_data['number']





#             rsvp_var = rsvp()
#             print(rsvp)

#             rsvp_var.date_added = datetime.now()
#             rsvp_var.event_id = event_id
#             rsvp_var.uniq_id = 'EL' + str(event_id)
#             rsvp_var.supplied_by = sitename
#             rsvp_var.attendee_name = name
#             rsvp_var.attendee_contact = number
#             rsvp_var.attendee_email = email
#             print(rsvp_var.uniq_id)
#             rsvp_var.save()


#             id = rsvp.objects.latest('table_id')
#             print('this is the latest id',id)

#             admin_log = AdminActionLog()

#             print(admin_log)
#             print(AdminActionLog)
#             # print('######################################### object created')
#             admin_log.admin_id = request.session['admin_id']
#             print('######################################################################################')
#             admin_log.timestamp = timezone.now()
#             admin_log.parameter = 'Added RSVP'
#             admin_log.event_id = event_id
#             print(rsvp_var.table_id)
#             admin_log.action_taken = "Added RSVP at id"+' '+str(rsvp_var.table_id)

#             #This is last inserted id
#             print(type(admin_log.action_taken))
#             print(admin_log.admin_id , admin_log.timestamp, admin_log.parameter, admin_log.event_id,  admin_log.action_taken)
#             admin_log.save()

#             print('successfully data added in ADMINACTIONLOG')



#             # connected user

#             con_user = []
#             for i in StatusPromotionTicketing.objects.all().filter(event_id= event_id):
#                 con_user.append(i)

#             print(con_user)
#             connected_user = 0
#             for i in con_user:
#                 connected_user = i.connected_user
#             print('connected user no',connected_user)

#             users = Users.objects.all().filter(id=connected_user)
#             print(users)
#             mail = ''
#             for j in users:
#                 mail = j.user

#             print('mail is ',mail)

#             article = Articles2.objects.all().filter(id = event_id)

#             event = ''

#             for i in article:
#                 event = i.event_name

#             print(event)


#             subject = sitename
#             message = 'Get in touch with the person by just replying to this email'

#             html_message = render_to_string('static/common/Add_rsvp_confirmation.html',
#                                                    {
#                                                        'name': name,
#                                                        'number': number,
#                                                        'email': email,
#                                                        'message':message,
#                                                        'event':event
#                                                    })



#             email_from = 'info@ercess.com'
#             recipient_list = [mail]
#             headers ={'Reply-To':email}

#             # send_mail(subject, message, email_from, recipient_list,html_message=html_message)

#             msg = EmailMessage(subject,html_message, email_from, recipient_list, headers={'Reply-To':email})
#             msg.content_subtype = "html"

#             msg.send(fail_silently=False)
#             print('mail is send to your account')

#             return redirect('admin-panel:details',event_id)


#     else:
#         form = AddRsvpForm()

#     return render(request, 'admin_panel/add_rsvp.html', {'form': form})

def send_pur_confirm_add_sales_email(event_name, recipient_list_par, amountpaid, quantity, attendee_name, attendee_contact_number, attendee_email_id, user_mail, booking_id, organization_name, location, contact_number, send_to, event_short_url):
    # send email on purchase ticket
    subject = 'Your ticket purchase confirmation - '+event_name
    # email_from = 'info@ercess.com'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [recipient_list_par]
    html_message = render_to_string('static/common/PURCHASE_CONFIRMATION.html', {
        'event_name': event_name,
        'amount_paid': amountpaid,
        'sold': quantity,
        'name': attendee_name,
        'contactnumber': attendee_contact_number,
        'email':attendee_email_id,
        'organizer_email': user_mail,
        'booking_id': booking_id,
        'organizer_name': organization_name,
        'organizer_location':location,
        'organization_contact_number':contact_number,
        'send_to':send_to,
        'event_short_url':event_short_url
    })
    msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'no-reply@ercess.com'})
    msg.content_subtype = "html"
    msg.send(fail_silently=False)

def add_sales(request, event_id):

    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    if request.method == 'POST':
        form = AddSalesDetailsForm(request.POST)
        if form.is_valid():
            ticket_name = form.cleaned_data['ticket_name']
            booking_id = form.cleaned_data['booking_id']
            purchase_date_time = form.cleaned_data['purchase_date_time']
            purchase_time = form.cleaned_data['purchase_time']
            amount_paid = form.cleaned_data['amount_paid']
            quantity = form.cleaned_data['quantity']
            attendee_name = form.cleaned_data['attendee_name']
            attendee_contact_number = form.cleaned_data['attendee_contact_number']
            attendee_email_id = form.cleaned_data['attendee_email_id']
            website_name = form.cleaned_data['websitename']
            referrerCode = form.cleaned_data['referrer_code']


            urlShortnerFilter = ShortUrlTracker.objects.filter(event_id=event_id,source='referral_marketing').values('short_url')
            if (len(urlShortnerFilter) != 0):
                event_short_url = list(urlShortnerFilter)[0]['short_url']
            else:
                event_short_url = ''


            # try:
            #     ticket = Tickets.objects.all().filter(event_id=event_id)
            #     eid = 0
            #     ticketid = 0
            #     for i in ticket:
            #         eid = i.event_id
            #         ticketid = i.tickets_id
            # except Tickets.DoesNotExist:
            #      raise Http404

            ticketFilterData = Tickets.objects.get(event_id=event_id, ticket_name=ticket_name)
            ticketid = ticketFilterData.tickets_id
            eid = event_id
            print(eid, ticketid)

            #connected user from status promotion ticketing table
            try:
                statusPromotions = StatusPromotionTicketing.objects.all().filter(event_id= event_id)

                connecteduser = 0
                for i in statusPromotions:
                    connecteduser = i.connected_user
            except StatusPromotionTicketing.DoesNotExist:
                raise Http404

            # email id of connected user from user table
            try:
                users = Users.objects.all().filter(id=connecteduser)
                user_mail = ''
                organization_name = str()
                contact_number = str()

                for i in users:
                    user_mail = i.user
                    organization_name = str(i.firstname) + ' ' + str(i.lastname)
                    contact_number = i.mobile



            except Users.DoesNotExist:
                raise Http404

            date = str(purchase_date_time)
            # print('date',purchase_date_time)
            # print('time',purchase_time)
            time = str(purchase_time)
            date = date[:-15]
            # print(date)

            new_date_time=str(date)+' ' +time

            # print('#########################', type(new_date_time),new_date_time)
            # if (new_date_time == None or new_date_time == ''):
            #     date_object = dt.now()
            # else:
            #     date_object = datetime.strptime(new_date_time, "%Y-%m-%d %H:%M:%S")
            try:
                # date_object = datetime.strptime(new_date_time, "%Y-%m-%d %H:%M:%S")
                date_object = datetime.strptime(new_date_time, "%Y-%m-%d %I:%M %p")
            except:
                date_object = dt.now()

            # print(date_object, ' >>>><<<< ', new_date_time)

            # ticketsale = Tickets_Sale()
            ticketsale = TicketsSale()
            ticketsale.event_id = eid
            ticketsale.ticket_id = ticketid
            ticketsale.oragnizer = connecteduser
            ticketsale.ticket_type = ticket_name
            ticketsale.booking_id = booking_id
            ticketsale.purchase_date = date_object
            # ticketsale.purchase_date = date_object            
            ticketsale.ampunt_paid = amount_paid
            ticketsale.qty = quantity
            ticketsale.attendee_name = attendee_name
            ticketsale.attendee_contact = attendee_contact_number
            ticketsale.attendee_email = attendee_email_id
            ticketsale.seller_site = website_name
            ticketsale.ticket_handover = 'mail sent'
            ticketsale.save()
            ticketSaleObject = TicketsSale.objects.all().last()

            expectations = ExpectationsFeedbacks.objects.create(event_id = event_id, booking_id = booking_id, email = attendee_email_id, expectation_msg = '', exp_mail_status = 'pending', feedback_msg = '', feedback_mail_status = 'pending', provided_for = 'expectation and feedback')

            # modify code
            event_table = Articles2.objects.get(id = event_id)
            event_name = str()
            location = str()

            event_name = event_table.event_name
            location = event_table.full_address
            # ends here ~ modify code

            #######################################################
            ############ Referral Code ~ Functionality ############
            ################## STARTS HERE ########################

            ticketDiscountFilter = TicketDiscounts.objects.filter(ticket_id=ticketid)
            
            # if tickets discount have data
            ########################################

            # check is attendee_email_id already have data in ReferrerCashbackInfo table
            isReferrerExistsFilter = ReferrerCashbackInfo.objects.filter(email_id=attendee_email_id).values()
            isReferrerExistsList = list(isReferrerExistsFilter)
            # ends here ~ check is attendee_email_id already have data in ReferrerCashbackInfo table

            if len(isReferrerExistsList) == 0: 
                # code works only if attendee_email_id doesn't exists in ReferrerCashbackInfo table

                # create unique referrer code
                uniqueReferrerCode = str(uuid.uuid4().hex[-2:].upper())+str(uuid.uuid4().hex[:6].upper())+str(uuid.uuid4().hex[:2].upper())
                # ends here ~ create unique referrer

                # create referral code for new attendee
                # ReferrerCashbackInfo.objects.create(referrer_code=uniqueReferrerCode,email_id=attendee_email_id,payable_amount=0,ticket_sales_id=0)
                ReferrerCashbackInfo.objects.create(number='',payment_platform='',referrer_code=uniqueReferrerCode,email_id=attendee_email_id,code_generated_on=dt.now())
                # ends here ~ create referral code for new attendee
            else:
                # code works only if attendee_email_id is exists in ReferrerCashbackInfo table
                uniqueReferrerCode =isReferrerExistsList[0]['referrer_code']



            # ends here ~ code works only if attendee_email_id is exists in ReferrerCashbackInfo table

            # query for filter data from different table to get organizer email
            filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=event_id).values('connected_user')
            connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']
            # ends here ~ query for filter data from different table to get organizer email

            # add leads into table
            saveLeadsData(attendee_name,attendee_email_id,attendee_contact_number, event_id, connectedUserId)
            # ends here ~ add leads into table

            # store required value in ticketDiscountCoupons
            if len(ticketDiscountFilter) == 0:
                ticketDiscountCoupons = ''
            else:
                ticketDiscountList = list(ticketDiscountFilter)
                ticketDiscountCoupons = ticketDiscountList

            # ends here ~ store required value in ticketDiscountCoupons

            # get cashback & discount amount
            ercessOffersFilter = ErcessOffers.objects.filter(status='active').values()
            ercessOffersList = list(ercessOffersFilter)
            if len(ercessOffersList) == 0:
                ercessOffersCashbackAmt = 0
                ercessOffersDiscountAmt = 0
            else:
                ercessOffersCashbackAmt = ercessOffersList[0]['cashback']
                ercessOffersDiscountAmt = ercessOffersList[0]['discount_amt'] 
            # ends here ~ get cashback & discount  amount

            statusPromoFilter = StatusPromotionTicketing.objects.get(event_id=event_id)
            referrerProgramStatus = statusPromoFilter.referrer_program_status

            # get referrer marketing url
            urlShortnerFilter = ShortUrlTracker.objects.filter(event_id=event_id,source='referral_marketing').values('short_url')
            if (len(urlShortnerFilter) != 0):
                shortUrl = list(urlShortnerFilter)[0]['short_url']
                referral_marketing_url = 'https://' + request.get_host() + '/rcss/'+ shortUrl
            else:
                referral_marketing_url = ''
            # ends here ~ get referrer marketing url
            
            if referrerProgramStatus == 1:
                # send all coupon code and referral code to attendee_email_id according to ticket_id
                subject = 'Referrer & Coupon Code for ' + event_name + ' Event'
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [attendee_email_id]
                html_message = render_to_string('static/common/referral_and_coupon_code_info.html', {
                    'event_name': event_name,
                    'referrer_code':uniqueReferrerCode,
                    'referrer_code_cashback':ercessOffersCashbackAmt,
                    'discount_coupons':ticketDiscountCoupons,
                    'discount_coupons_amt':ercessOffersDiscountAmt,
                    'referral_marketing_url': referral_marketing_url
                })
                msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': attendee_email_id})
                msg.content_subtype = "html"
                msg.send(fail_silently=False)
                # ends here ~ send all coupon code and referral code to attendee_email_id according to ticket_id

                # send email if referral code exists in our db (send a link to fill form for cashback)
                try:
                    # get referrer email
                    ReferrerCashbackFilter = ReferrerCashbackInfo.objects.get(referrer_code=referrerCode)
                    attendeeEmailIdCashback = ReferrerCashbackFilter.email_id
                    # ends here ~ get referrer email

                    if attendee_email_id != attendeeEmailIdCashback: 
                        # generate & save token in db
                        timeInMilliseconds = int(round(Time.time() * 1000))
                        tokenCashbackEmail = str(timeInMilliseconds)+str(uuid.uuid4().hex[:4].upper())
                        cashback_mobile_url = 'http://' + request.get_host() + '/live/cashback-info/' + tokenCashbackEmail
                        # ends here ~ generate & save token in db

                        # get cashback amount
                        ercessOffersFilter = ErcessOffers.objects.filter(status='active').values()
                        ercessOffersList = list(ercessOffersFilter)
                        if(len(ercessOffersList) == 0):
                            ercessOffersCashbackAmt = 0 
                        else:
                            ercessOffersCashbackAmt = ercessOffersList[0]['cashback'] 
                        # ends here ~ get cashback amount

                        # update ReferrerCashbackInfo table if referrer code matches (which is provided by new attendee)
                        # ercessOffersCashbackAmt = ReferrerCashbackFilter.payable_amount + ercessOffersCashbackAmt
                        # ReferrerCashbackInfo.objects.filter(referrer_code=referrerCode).update(payable_amount=ercessOffersCashbackAmt)
                        # ends here ~ update ReferrerCashbackInfo table if referrer code matches (which is provided by new attendee)
                        
                        # store referrer email with token
                        ReferrerCashbackTokens.objects.create(token_code=tokenCashbackEmail,attendee_email_id=attendeeEmailIdCashback)
                        # ends here ~ store referrer email with token

                        # store values in TicketSalesReference table to track referrer code purchases and other things 
                        TicketSalesReference.objects.create(booking_id=booking_id,event_id=event_id,used_referred_code=referrerCode,cashback_to_process=ercessOffersCashbackAmt,cashback_process_status='')
                        # ends here ~ store values in TicketSalesReference table to track referrer code purchases and other things

                        # send email to get payment details
                        subject = 'Congratulations! One Purchase made through Your Referrer Code'
                        email_from = settings.EMAIL_HOST_USER
                        recipient_list = [attendeeEmailIdCashback]
                        html_message = render_to_string('static/common/cashback_payment_link.html', {
                            'cashback_mobile_url': cashback_mobile_url
                        })
                        msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': attendeeEmailIdCashback})
                        msg.content_subtype = "html"
                        msg.send(fail_silently=False)
                        # ends here ~ send email to get payment details
                    

                except Exception as e:
                    print('Our Records does not have such Referral Code : ',e)
                # ends here ~ send email if referral code exists in our db (send a link to fill form for cashback)


                ########################################
                # ends here ~ if tickets discount have data

            ################### ENDS HERE #########################
            ############ Referral Code ~ Functionality ############
            #######################################################

            ''' payment table data are adding here '''
            eve = TicketsSale.objects.all().filter(event_id=event_id)
            amountpaid = float()
            ticket_sale_id = str()
            for i in eve:
                ticket_sale_id = i.table_id
                amountpaid = i.ampunt_paid

            # print('type of amount ', amountpaid, type(amountpaid))

            partner_site = PartnerSites.objects.all().filter(site_name = website_name)

            negotiated_convenience_fees = float()
            negotiated_transaction_fees = float()
            negotiated_tax_charges = float()
            negotiated_flat_charges = float()


            for data in partner_site:
                partner_id = data.table_id
                if data.negotiated_transaction_fee == '':
                    negotiated_transaction_fees = 0.0
                else:
                    negotiated_transaction_fees = float(data.negotiated_transaction_fee)

                if data.negotiated_convenience_fee == '':
                    negotiated_convenience_fees = 0.0

                else:
                    negotiated_convenience_fees = float(data.negotiated_convenience_fee)

                if data.negotiated_flat_charges == '':
                    negotiated_flat_charges = 0.0
                else:
                    negotiated_flat_charges = float(data.negotiated_flat_charges)

                if data.negotiated_tax_charges == '':
                    negotiated_tax_charges = 0.0

                else:
                    negotiated_tax_charges = float(data.negotiated_tax_charges)
            sum_in_percentage = negotiated_convenience_fees + negotiated_transaction_fees + negotiated_tax_charges
            print(amountpaid, ' >> << ',sum_in_percentage)
            if (amountpaid != None and amountpaid != ''):
                deduct_sum_percentage = amountpaid - (amountpaid*sum_in_percentage/100)
                expected_amnt_partner = deduct_sum_percentage - negotiated_flat_charges
                # @author Shubham
                expected_amnt_partner = round(expected_amnt_partner, 2)
                # ends here ~ @author Shubham
            else:
                expected_amnt_partner = None

            payment_table = PaymentSettlement()
            payment_table.date_added = datetime.now()
            payment_table.date_modified = datetime.now()
            payment_table.booking_id = booking_id
            payment_table.ticket_sale_id = ticket_sale_id
            payment_table.added_by = request.session['admin_id']
            payment_table.modified_by = request.session['admin_id']
            payment_table.receival_status = 'pending'
            payment_table.expected_amnt_partner = expected_amnt_partner
            payment_table.rcvd_amnt_partner = 0
            payment_table.receival_date = None
            payment_table.receival_invoice = ''
            payment_table.partner_dispute = ''
            payment_table.process_status = 'pending'
            payment_table.amount_processed = 0
            payment_table.process_date = None
            payment_table.organizer_dispute = ''
            payment_table.save()

            # event_table = Articles2.objects.get(id = event_id)
            # event_name = str()
            # location = str()



            # event_name = event_table.event_name
            # location = event_table.full_address

            # # send all coupon code and referral code to attendee_email_id
            # subject = 'Referrer & Coupon Code for ' + event_name + ' Event'
            # email_from = settings.EMAIL_HOST_USER
            # recipient_list = [attendee_email_id]
            # html_message = render_to_string('static/common/referral_and_coupon_code_info.html', {
            #     'event_name': event_name,
            #     'referrer_code':uniqueReferrerCode,
            #     'discount_coupons':ticketDiscountList
            # })
            # msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': attendee_email_id})
            # msg.content_subtype = "html"
            # msg.send(fail_silently=False)
            # # ends here ~ send all coupon code and referral code to attendee_email_id


            subject = 'TICKET SALE ALERT - '+event_name
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user_mail, 'track@ercess.com']
            # headers = {'Reply-To': attendee_email_id}

            # send_mail(subject, message, email_from, recipient_list)

            html_message = render_to_string('static/common/new_sales_to_organizers.html',
                                            {
                                                'event_name': event_name,
                                                'revenue': amount_paid,
                                                'sold': quantity,
                                                'name': attendee_name,
                                                'contactnumber': attendee_contact_number,
                                                'email': attendee_email_id,
                                                'booking_id': booking_id,
                                                'ticket_name': ticket_name
                                            })

            msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': attendee_email_id})
            msg.content_subtype = "html"
            msg.send(fail_silently=False)
            ##################################################

            # set variable to N/A, if variable is empty
            if (attendee_contact_number == '' or attendee_contact_number == None):
                attendee_contact_number = 'N/A'
            if (attendee_email_id == '' or attendee_email_id == None):
                attendee_email_id = 'N/A'
            if (attendee_name == '' or attendee_name == None):
                attendee_name = 'N/A'
            # ends here ~ set variable to N/A, if variable is empty

            # # send email on purchase ticket

            if attendee_email_id == 'N/A':
                # recipient_list = ['track@ercess.com']
                send_pur_confirm_add_sales_email(event_name, 'track@ercess.com', amountpaid, quantity, attendee_name, attendee_contact_number, attendee_email_id, user_mail, booking_id, organization_name, location, contact_number, 'organizer', event_short_url)
            else:
                # recipient_list = [attendee_email_id, 'track@ercess.com']
                send_pur_confirm_add_sales_email(event_name, attendee_email_id, amountpaid, quantity, attendee_name, attendee_contact_number, attendee_email_id, user_mail, booking_id, organization_name, location, contact_number, 'attendee', event_short_url)
                send_pur_confirm_add_sales_email(event_name, 'track@ercess.com', amountpaid, quantity, attendee_name, attendee_contact_number, attendee_email_id, user_mail, booking_id, organization_name, location, contact_number, 'organizer', event_short_url)
            # subject = 'Your ticket purchase confirmation - '+event_name
            # # email_from = 'info@ercess.com'
            # email_from = settings.EMAIL_HOST_USER
            # if attendee_email_id == 'N/A':
            #     recipient_list = ['track@ercess.com']
            # else:
            #     recipient_list = [attendee_email_id, 'track@ercess.com']
            # html_message = render_to_string('static/common/PURCHASE_CONFIRMATION.html',
            #                                 {
            #                                     'event_name': event_name,
            #                                     'amount_paid': amountpaid,
            #                                     'sold': quantity,
            #                                     'name': attendee_name,
            #                                     'contactnumber': attendee_contact_number,
            #                                     'email':attendee_email_id,
            #                                     'organizer_email': user_mail,
            #                                     'booking_id': booking_id,
            #                                     'organizer_name': organization_name,
            #                                     'organizer_location':location,
            #                                     'organization_contact_number':contact_number
            #                                 })
            # msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'no-reply@ercess.com'})
            # msg.content_subtype = "html"
            # msg.send(fail_silently=False)
            return redirect('admin-panel:details', event_id)



    else:
        # @author Shubham
        form = AddSalesDetailsForm(event_id = event_id)
        # ends here ~ @author Shubham


    return render(request, 'admin_panel/add_sales.html',{'form': form})

class sale_settled(View):
    def get(self,request):
        if 'admin_id' not in request.session.keys():
            return redirect('/admin-site/login')

        ''' model is used to fetch the event Name '''
        ticketsale =TicketsSale.objects.all().order_by('-ticket_id')
        booking_id = list()
        amount_paid = list()
        purchase_date = list()
        attendee_name = list()
        event_id = list()
        table_id = list()
        payment_receival = list()
        payment_process =list()

        for ticket  in ticketsale:
            booking_id_temp = ticket.booking_id
            table_id_temp = ticket.table_id
            payment = PaymentSettlement.objects.filter(ticket_sale_id = table_id_temp, booking_id = booking_id_temp)
            if payment.exists():
                payment = payment.values()
                if payment[0]['receival_status'] == 'settled' and payment[0]['process_status'] == 'settled':
                    table_id.append(ticket.table_id)
                    booking_id.append(ticket.booking_id)
                    amount_paid.append(ticket.ampunt_paid)
                    purchase_date.append(ticket.purchase_date)
                    attendee_name.append(ticket.attendee_name)
                    event_id.append(ticket.event_id)
                    payment_receival.append(payment[0]['receival_status'])
                    payment_process.append(payment[0]['process_status'])

        event_name = list()
        article_list = list()
        if event_id:
            for id in event_id:
                article_list.append(Articles2.objects.get(id=id))

        
        for i in article_list:
            event_name.append(i.event_name)

        # print(article_list)
        sales = zip(booking_id, amount_paid, purchase_date, attendee_name,event_name,table_id,event_id)#,payment_receival,payment_process)
        if len(table_id) == 0:
            return redirect('/admin-site/sale-pending')
        else:
            return render(request, 'admin_panel/sale_settled.html',{'sales': sales})

class sale_pending(View):
    def get(self,request):
        if 'admin_id' not in request.session.keys():
          return redirect('/admin-site/login')

        ''' model is used to fetch the event Name '''
        ticketsale = TicketsSale.objects.all().order_by('-ticket_id')
        booking_id = list()
        amount_paid = list()
        purchase_date = list()
        attendee_name = list()
        event_id = list()
        table_id = list()
        payment_receival = list()
        payment_process = list()
        for ticket  in ticketsale:
            booking_id_temp = ticket.booking_id
            table_id_temp = ticket.table_id            
            payment = PaymentSettlement.objects.filter(ticket_sale_id = table_id_temp, booking_id = booking_id_temp)
            if payment.exists():
                payment = payment.values()
                if payment[0]['receival_status']  != 'settled' or payment[0]['process_status'] != 'settled' :
                    table_id.append(ticket.table_id)
                    booking_id.append(ticket.booking_id)
                    amount_paid.append(ticket.ampunt_paid)
                    purchase_date.append(ticket.purchase_date)
                    attendee_name.append(ticket.attendee_name)
                    event_id.append(ticket.event_id)
                    payment_receival.append(payment[0]['receival_status'])
                    payment_process.append(payment[0]['process_status'])

        event_name = list()
        article_list = list()
        for id in event_id:
            article_list.append(Articles2.objects.get(id=id))


        for i in article_list:
             event_name.append(i.event_name)
        # print(event_id)

        # print(article_list)
        # print(event_name)
        print(booking_id, amount_paid, purchase_date, attendee_name,event_name,table_id,event_id,payment_receival,payment_process)
        sales = zip(booking_id, amount_paid, purchase_date, attendee_name,event_name,table_id,event_id,payment_receival,payment_process)

        return render(request, 'admin_panel/sale_pending.html',{'sales': sales})


class email_marketing(View):
    def get(self,request):
        if 'admin_id' not in request.session.keys():
          return redirect('/admin-site/login')

        ''' model is used to fetch the CampaignTemplates data '''


        all_data = CampaignTemplates.objects.all()

        return render(request, 'admin_panel/email_marketing.html',{'data': all_data})

def email_marketing_detail(request,id):
    if 'admin_id' not in request.session.keys():
      return redirect('/admin-site/login')

    ''' model is used to fetch the CampaignTemplates data '''

    all_data = CampaignStatus.objects.filter(campaign_id=id)
    return render(request, 'admin_panel/email_marketing_detail.html',{'data': all_data})

class sms_marketing(View):
    def get(self,request):
        if 'admin_id' not in request.session.keys():
          return redirect('/admin-site/login')

        ''' model is used to fetch the sms_marketing data '''

        all_data = CampaignTemplates.objects.all()

        return render(request, 'admin_panel/sms_marketing.html',{'data': all_data})

class leads(View):
    def get(self,request):
        if 'admin_id' not in request.session.keys():
          return redirect('/admin-site/login')

        ''' model is used to fetch the sms_marketing data '''

        data = Leads.objects.all()

        all_data=[]

        for i in data:
            resp={}
            try:
                resp['category'] = Categories.objects.get(category_id=i.category).category
            except Exception as e:
                resp['category'] = ''

            try:
                resp['sub_category'] = Topics.objects.get(topics_id=i.sub_category).topic
            except Exception as e:
                resp['sub_category'] = ''

            resp['name'] = i.name
            resp['email'] = i.email
            resp['contact'] = i.contact
            resp['city'] = i.city
            resp['user_id'] = i.user_id
            resp['date_added'] = i.date_added
            all_data.append(resp)



        return render(request, 'admin_panel/leads.html',{'data': all_data})

def sms_marketing_detail(request,id):
    if 'admin_id' not in request.session.keys():
      return redirect('/admin-site/login')

    ''' model is used to fetch the CampaignTemplates data '''

    all_data = CampaignStatus.objects.filter(campaign_id=id)

    return render(request, 'admin_panel/sms_marketing_detail.html',{'data': all_data})

def payment_settlement(request,booking_id):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')
    payment = PaymentSettlement.objects.get(booking_id=booking_id )
    if request.method == 'POST':
        instance = get_object_or_404(PaymentSettlement, booking_id= booking_id)
        form = edit_paymentsettlement(request.POST,instance=instance)

        if form.is_valid():
            form.save(commit=True)
            messages.success(request, 'Form submission successful')
            return redirect('/admin-site/sale-settled') 
    else:
        form =  edit_paymentsettlement(initial={'booking_id':payment.booking_id,
                                                'receival_status':payment.receival_status,
                                                'expected_amnt_partner':payment.expected_amnt_partner,
                                                'rcvd_amnt_partner':payment.rcvd_amnt_partner,
                                                'receival_date':payment.receival_date,
                                                'receival_invoice':payment.receival_invoice,
                                                'partner_dispute':payment.partner_dispute,
                                                'process_status':payment.process_status,
                                                'amount_processed':payment.amount_processed,
                                                'amount_process_date':payment.amount_process_date,
                                                'organizer_dispute':payment.organizer_dispute,
                                                'process_invoice':payment.process_invoice})
    return render(request, 'admin_panel/payment_settlement.html', {'form': form})


def sale_details(request,table_id):
    sales = TicketsSale.objects.get(table_id=table_id)
    payment = PaymentSettlement.object.get(ticket_sale_id = table_id)
    receival_status = payment.receival_status
    process_status = payment.process_status
    return render(request,'admin_panel/sale-details.html',{'sales':sales, 'payment':payment})


def booking_details(request,booking_id):
    tickets_sale=TicketsSale.objects.get(booking_id=booking_id)
    payment_settlement_table=PaymentSettlement.objects.get(booking_id=booking_id)
    event_id = tickets_sale.event_id
    status = StatusPromotionTicketing.objects.get(event_id=tickets_sale.event_id)
    user_id = status.connected_user
    bankdetails = BankDetails.objects.get(user_id=user_id)
    if bankdetails is not None:
        try:
            user=Users.objects.get(id=user_id)
            content={
            'tickets_sale':tickets_sale,
            'payment_settlement':payment_settlement_table,
            'name':user.user,
            'event_id':event_id,
            'bankdetails':bankdetails
            }
            return render(request, 'admin_panel/event-details-page.html', content)
        except Users.DoesNotExist:
            print('no user exist')
    # if user bank details are missing
    content={
    'tickets_sale':tickets_sale,
    'payment_settlement':payment_settlement_table,
    'event_id': event_id
        }
    return render(request,'admin_panel/event-details-page.html',content)


def partner_site_details(request,table_id):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    partner = PartnerSites.objects.get(table_id=table_id)
    #########################################
    """  partner's category """
    try:
        partners_site=ErcessPartnersCategories.objects.get(table_id=table_id)
    except ObjectDoesNotExist:
        partners_site=0

    ##########################################
    """ partner's curencies """
    try:
        currency=PartnerCurrencies.objects.get(table_id=table_id)
    except ObjectDoesNotExist:
        currency=0
    ############################################
    """ Indiave states ercess """
    # try:
    #     states=ErcessIndiaeveStates.objects.get(table_id=table_id)
    # except ObjectDoesNotExist:
    #     states=0
    ##############################################
    """ TimeZones """
    if currency!=0:
        try:
            timezones=PartnerTimezones.objects.filter(partner_id=currency.partner_id)
        except ObjectDoesNotExist:
            timezones=0
        timez=[]
        if timezones:
            if len(timezones)>1:
                for time in timezones:
                    timez.append(time.timezone)
                timezone=', '.join(timez)
            else:
                timezone=timezones[0].timezone
    else:
        timezone=''
    ##############################################
    """ ercess other mappings """
    ercess_other=0
    try:
        ercess_other=ErcessOtherMappings.objects.get(table_id=table_id)
    except ObjectDoesNotExist:
        ercess_other=0
    ##############################################
    """ partner's subcategories """
    partner_sub=[]
    try:
        sub=ErcessPartnersSubcategories.objects.all()
        partner_sub.append(sub)
    except ObjectDoesNotExist:
        partner_sub.append('')


    return render(request,'admin_panel/partner-sites-details.html',{'partners_site':partner,'partner_cat':partners_site,\
    'currency':currency,'ercess_other':ercess_other,'timezone':timezone, 'table_id':table_id})

def details_promotion_status(request,table_id):
    if 'admin_id' not in request.session.keys():
        return redirect('/admin-site/login')

    promotion_links = EventStatusOnChannel.objects.filter(site_id=table_id).order_by('-event_id')

    upcoming_events=[]
    past_ongoing_events=[]
    for promo in promotion_links:
        data = {}
        event = Articles2.objects.get(id=promo.event_id)
        data['last_updated']=promo.last_updated
        try:
            data['event_name'] = event.event_name
        except Exception as e:
            data['event_name'] = ''

        data['site_id']=promo.site_id
        data['event_id']=promo.event_id
        data['link']=promo.link
        data['promotion_status']=promo.promotion_status
        data['partner_status']=promo.partner_status

        if event.sdate > timezone.now():
            upcoming_events.append(data)
        else:
            past_ongoing_events.append(data)

    site = PartnerSites.objects.get(table_id = table_id)
    context = {
        "upcoming_events":upcoming_events,
        "past_ongoing_events": past_ongoing_events,
        "site": site
    }
    return render(request,'admin_panel/details_promotion_status.html',context)

# class UserRegister(generic.View):

#     form_class = AddUserForm
#     template_name = 'admin_panel/add_user.html'

#     def get(self,request):
#         form = self.form_class(None)
#         return render(request,self.template_name,{'form':form})



#     def post(self,request):
#         form = self.form_class(request.POST)

#         if form.is_valid():
#             post = form.save(commit = False)

#             st = post.email
#             h = hashlib.md5(st.encode())
#             post.md5 = h.hexdigest()


#             alpha = string.ascii_letters + string.digits
#             passw = ''.join(random.choice(alpha) for i in range(8))
#             x = hashlib.md5(passw.encode())
#             post.password = x.hexdigest()

#             subject = "Thanks for registration"
#             text_content = "Hi {}, you have successfully registered.Here is your login password - {}".format(post.first_name,passw)
#             from_mail = settings.EMAIL_HOST_USER
#             to = post.email


#             msg = EmailMultiAlternatives(subject, text_content, from_mail, [to],cc = ["track@ercess.com"] )
#             msg.send(fail_silently=True)

#             post.save()



#         return render(request,self.template_name,{'form':form})




# @author Shubham ~ October 11 2019
from django.views.decorators.csrf import csrf_exempt


# function for send email to organizer (owner) on add rsvp
def mailOnAddRspv(unlockRsvpUrlParam,eventIdPar, eventPar, namePar, contactPar, attendeeEmailPar, messagePar, organizerEmailPar,leadPackagePar, isDetailsLockedPar):
    try:
        # if variable is blank then set variable value equal to 'N/A'
        if eventPar == '' or eventPar == None:
            eventPar = 'N/A'
        if namePar == '' or namePar == None:
            namePar = 'N/A'
        if contactPar == '' or contactPar == None:
            contactPar = 'N/A'
        if messagePar == '' or messagePar == None:
            messagePar = 'N/A'
        if attendeeEmailPar == '' or attendeeEmailPar == None:
            attendeeEmailPar = 'N/A'
        # ends here ~ if variable is blank then set variable value equal to 'N/A'


        unlockRsvpCompleteUrl = unlockRsvpUrlParam
        
        subject = '[ALERT] New lead received - ' + eventPar
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [organizerEmailPar]
        html_message = render_to_string('static/common/Add_rsvp_confirmation.html', {
            'event': eventPar,
            'event_name': eventPar,
            'name': namePar,
            'number': contactPar,
            'email': attendeeEmailPar,
            'message': messagePar,
            'lead_package':leadPackagePar,
            'is_details_locked':isDetailsLockedPar,
            'unlock_rsvp_url':unlockRsvpCompleteUrl
        })

        msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
        msg.content_subtype = "html"
        msg.send(fail_silently=False)

    except Exception as e:
        print('error while send email to organizer >> ',e)
# ends here ~ function for send email to organizer (owner) on add rsvp

def saveLeadsData(leadsName,leadsEmail,leadsContact, event_id, userId):
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
    leadsFilter = Leads.objects.filter(contact=leadsContact,category=catId,city=articleCityName)
    if len(leadsFilter) == 0:
        Leads.objects.create(name=leadsName,email=leadsEmail,contact=leadsContact,category=catId,sub_category=topicId,city=articleCityName,user_id=userId)


@csrf_exempt
def add_rsvp_details(request, event_id):
    try:
        if 'admin_id' not in request.session.keys():
            return redirect('/admin-site/login')

        if request.method == 'POST':
            attendee_name = request.POST["attendee_name"]
            attendee_email = request.POST["attendee_email"]
            attendee_contact = request.POST["attendee_contact"]
            supplied_by = request.POST["supplied_by"]
            message = request.POST["message"]

            # check rsvp exists or not
            rsvpFilter = Rsvp.objects.filter(attendee_email=attendee_email,event_id=event_id)
            if(len(rsvpFilter) > 0):
                return HttpResponseRedirect(reverse('admin-panel:details', kwargs={'event_id':event_id}))
            # ends here ~ check rsvp exists or not

            # get leads_package values from Status Promotion Ticketing Table
            filterLeadPackage = StatusPromotionTicketing.objects.filter(event_id=event_id).values('leads_package')
            leadPackage = list(filterLeadPackage)[0]['leads_package']
            # ends here ~ get leads_package values from Status Promotion Ticketing Table



            if leadPackage == 0:

                # store data in rsvp table with certain conditions if leads_package = 0
                filterRsvpData = Rsvp.objects.filter(event_id=event_id)


                if len(filterRsvpData) < 2:
                    Rsvp.objects.create(attendee_name=attendee_name,attendee_email=attendee_email,attendee_contact=attendee_contact,supplied_by=supplied_by,message=message,locked=0,event_id=event_id)

                    # data for send email to owner
                    attendee_name_owner_email = attendee_name
                    attendee_email_owner_email = attendee_email
                    attendee_contact_owner_email = attendee_contact
                    message_owner_email = message
                    is_details_locked = 0
                    # ends here ~ data for send email to owner

                else:
                    Rsvp.objects.create(attendee_name=attendee_name,attendee_email=attendee_email,attendee_contact=attendee_contact,supplied_by=supplied_by,message=message,locked=1,event_id=event_id)
                    is_details_locked = 1
                    # data for send email to owner
                    if attendee_name != '':
                        attendee_name_owner_email = attendee_name[0]+'xxxxxxxxx'
                    else:
                        attendee_name_owner_email = attendee_name

                    if attendee_email != '':
                        attendee_email_owner_email = attendee_email[0]+'xxxxxxxxx'
                    else:
                        attendee_email_owner_email = attendee_email

                    if attendee_contact != '':
                        attendee_contact_owner_email = attendee_contact[0]+'xxxxxxxxx'
                    else:
                        attendee_contact_owner_email = attendee_contact

                    if message != '':
                        message_owner_email = message[0]+'xxxxxx xxx xxxx...'
                    else:
                        message_owner_email = message
                    # ends here ~ data for send email to owner
                    return HttpResponseRedirect(reverse('admin-panel:details', kwargs={'event_id':event_id}))
                


                # ends here ~ store data in rsvp table with certain conditions if leads_package = 0

            else:
                # store data in rsvp table without certain conditions if leads_package = 1
                Rsvp.objects.create(attendee_name=attendee_name,attendee_email=attendee_email,attendee_contact=attendee_contact,supplied_by=supplied_by,message=message,locked=0,event_id=event_id)

                is_details_locked = 0
                # data for send email to owner
                attendee_name_owner_email = attendee_name
                attendee_email_owner_email = attendee_email
                attendee_contact_owner_email = attendee_contact
                message_owner_email = message
                # ends here ~ data for send email to owner

                # ends here ~ store data in rsvp table without certain conditions if leads_package = 1

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

            # query for filter data from different table to get organizer email
            filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=event_id).values('connected_user')
            connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']

            filterUserData = Users.objects.get(id = connectedUserId)
            organizerEmail = filterUserData.user
            # ends here ~ query for filter data from different table to get organizer email


            # save rsvp personal data to additional leads table
            saveLeadsData(attendee_name,attendee_email,attendee_contact, event_id,connectedUserId)
            # Leads.objects.create(name=attendee_name,email=attendee_email,contact=attendee_contact,category=catId,sub_category=topicId,city=articleCityName)
            # ends here ~ save rsvp personal data to additional leads table

            
            # code to send a email to owner of event
            reverseUrlUnlockRsvp = reverse('dashboard:show-rsvp-premium-packages', kwargs={'event_id':event_id, 'service_type':'unlock_rsvp', 'purpose_of_payment':'unlock_event_rsvp'})
            unlockRsvpCompleteUrl = 'http://' + request.get_host() + str(reverseUrlUnlockRsvp)

            mailOnAddRspv(unlockRsvpCompleteUrl, event_id, articleEventName,attendee_name_owner_email,attendee_contact_owner_email,attendee_email_owner_email,message_owner_email,organizerEmail,leadPackage,is_details_locked)
            # ends here ~ code to send a email to owner of event
            
            return HttpResponseRedirect(reverse('admin-panel:details', kwargs={'event_id':event_id}))
    except Exception as e:
        print('error in add_rsvp_details >> ',e)
        return HttpResponseRedirect(reverse('admin-panel:details', kwargs={'event_id':event_id}))
        # return HttpResponseRedirect('/admin-site/add-sales-free-tkt-details/' + str(event_id))


# ends here ~ @author Shubham ~ October 11 2019

# ends here ~ @author Shubham ~ December 09 2019
@csrf_exempt
def add_sales_free_tkt_details(request, event_id):
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.')
    try:
        if 'admin_id' not in request.session.keys():
            return redirect('/admin-site/login')

        if request.method == 'POST':
            attendee_name = request.POST["attendee_name"]
            attendee_email = request.POST["attendee_email"]
            attendee_contact = request.POST["attendee_contact"]
            totalFreeTktQty = request.POST["totalFreeTktQty"]
            freeTktBookingId = request.POST["freeTktBookingId"]

            if attendee_name == None:
                attendee_name = ''
            if attendee_email == None:
                attendee_email = ''
            if attendee_contact == None:
                attendee_contact = ''
            if totalFreeTktQty == None:
                totalFreeTktQty = ''
            if freeTktBookingId == None:
                freeTktBookingId = ''

            # query for filter data from different table to get organizer email
            filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=event_id).values('connected_user')
            connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']

            connecteduser = connectedUserId

            users = Users.objects.get(id=connecteduser)
            user_mail = users.user
            organization_name = str(users.firstname) + ' ' + str(users.lastname)
            contact_number = users.mobile
            # ends here ~ query for filter data from different table to get organizer email

            # get required information from articles2 table
            event_table = Articles2.objects.get(id = event_id)
            event_name = event_table.event_name
            location = event_table.full_address
            # ends here ~ get required information from articles2 table

            # set val for store data and send email
            amount_paid = 0
            quantity = totalFreeTktQty
            # ends here ~ set val for store data and send email
          
            # save data to ticket sales table
            ticketSaleId = TicketsSale.objects.create(event_id=event_id,ticket_id=0,booking_id=freeTktBookingId,oragnizer=connectedUserId,purchase_date=dt.now(),ampunt_paid=amount_paid,qty=totalFreeTktQty,attendee_name=attendee_name,attendee_contact=attendee_contact,attendee_email=attendee_email,seller_site='',ticket_handover='')
            # ends here ~ save data to ticket sales table 

            # add data to PaymentSettlement
            PaymentSettlement.objects.create(date_added = dt.now(),date_modified = dt.now(),booking_id = freeTktBookingId,ticket_sale_id = ticketSaleId,added_by = request.session['admin_id'],modified_by = request.session['admin_id'],receival_status = 'settled',expected_amnt_partner = 0, rcvd_amnt_partner = 0, receival_date = dt.now(), receival_invoice = '', partner_dispute = '', process_status = 'settled', amount_processed = 0, amount_process_date = dt.now(), organizer_dispute = '')
            # ends here ~ add data to PaymentSettlement

              ################### expectations feedbacks   ######################### 

            expectations = ExpectationsFeedbacks.objects.create(event_id = event_id, booking_id = freeTktBookingId, email = attendee_email, expectation_msg = '', exp_mail_status = 'pending', feedback_msg = '', feedback_mail_status = 'pending', provided_for = 'expectation and feedback')

            attendee_email_id = attendee_email
            attendee_contact_number = attendee_contact

            # add leads into table
            saveLeadsData(attendee_name,attendee_email_id,attendee_contact_number, event_id, connectedUserId)
            # ends here ~ add leads into table

            ##########################################
            # send email on sales (free ticket)

            subject = 'TICKET SALE ALERT - '+event_name
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user_mail, 'track@ercess.com']
            # headers = {'Reply-To': attendee_email_id}

            # send_mail(subject, message, email_from, recipient_list)

            # html_message = render_to_string('static/common/new_sales_to_organizers.html', {
            #     'event_name': event_name,
            #     'revenue': amount_paid,
            #     'sold': quantity,
            #     'name': attendee_name,
            #     'contactnumber': attendee_contact_number,
            #     'email': attendee_email_id,
            #     'booking_id': 'N/A',
            #     'ticket_name': 'N/A'
            # })
            html_message = render_to_string('static/common/new_sales_free_tkt_to_organizers.html', {
                'event_name': event_name,
                'total_purchase_qty': totalFreeTktQty,
                'total_people_qty': totalFreeTktQty,
                'name': attendee_name,
                'contactnumber': attendee_contact_number,
                'email': attendee_email_id,
                'booking_id': freeTktBookingId
            })

            msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': attendee_email_id})
            msg.content_subtype = "html"
            msg.send(fail_silently=False)

            # set variable to N/A, if variable is empty
            if (attendee_contact_number == '' or attendee_contact_number == None):
                attendee_contact_number = 'N/A'
            if (attendee_email_id == '' or attendee_email_id == None):
                attendee_email_id = 'N/A'
            if (attendee_name == '' or attendee_name == None):
                attendee_name = 'N/A'
            # ends here ~ set variable to N/A, if variable is empty

            # send email on purchase ticket
            subject = 'Your ticket purchase confirmation - '+event_name
            # email_from = 'info@ercess.com'
            email_from = settings.EMAIL_HOST_USER
            if attendee_email_id == 'N/A':
                recipient_list = ['track@ercess.com']

            else:
                recipient_list = [attendee_email_id, 'track@ercess.com']
        
            html_message = render_to_string('static/common/PURCHASE_CONFIRMATION.html', {
                'event_name': event_name,
                'amount_paid': amount_paid,
                'sold': quantity,
                'name': attendee_name,
                'contactnumber': attendee_contact_number,
                'email':attendee_email_id,
                'organizer_email': user_mail,
                'booking_id': freeTktBookingId,
                'organizer_name': organization_name,
                'organizer_location':location,
                'organization_contact_number':contact_number
            })
            msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': attendee_email_id})
            msg.content_subtype = "html"
            msg.send(fail_silently=False)

            # ends here ~ send email on sales (free ticket)
            ###################################################


            return HttpResponseRedirect(reverse('admin-panel:details', kwargs={'event_id':event_id}))
            # return HttpResponse('/admin-site/add-sales-free-tkt-details/' + str(event_id))
        else:
            return HttpResponseRedirect(reverse('admin-panel:details', kwargs={'event_id':event_id}))
    except Exception as e:
        print('error in add_sales_free_tkt_details >> ',e)
        return HttpResponseRedirect(reverse('admin-panel:details', kwargs={'event_id':event_id}))
        
# ends here ~ @author Shubham ~ December 09 2019

# @author Shubham ~ Send Confirmation Email to Organizer ~ October 12 2019
@csrf_exempt
def send_confirm_org_email(request):
    try:
        tableId = request.POST['tableId']

        # filter and extract required data from TicketSale Table
        filterTicketSale = TicketsSale.objects.get(table_id = tableId)

        eventId = filterTicketSale.event_id
        amountPaid = filterTicketSale.ampunt_paid
        ticketSoldQty = filterTicketSale.qty
        attendeeName = filterTicketSale.attendee_name
        attendeeContactNumber = filterTicketSale.attendee_contact
        attendeeEmail = filterTicketSale.attendee_email
        bookingId = filterTicketSale.booking_id
        ticketName = filterTicketSale.ticket_type
        organizerId = filterTicketSale.oragnizer

        # ends here ~ filter and extract required data from TicketSale Table

        # filter and extract required data from Articles2 Table
        filterEventData = Articles2.objects.get(id = eventId)
        eventName = filterEventData.event_name
        # ends here ~ filter and extract required data from Articles2 Table

         # filter and extract required data from Users Table
        filterUserData = Users.objects.get(id = organizerId)
        organizerEmail = filterUserData.user
        # ends here ~ filter and extract required data from Users Table

        # set variable to N/A, if variable is empty
        if (attendeeContactNumber == '' or attendeeContactNumber == None):
            attendeeContactNumber = 'N/A'
        if (attendeeEmail == '' or attendeeEmail == None):
            attendeeEmail = 'N/A'
        if (attendeeName == '' or attendeeName == None):
            attendeeName = 'N/A'
        # ends here ~ set variable to N/A, if variable is empty

        # send email to organizer
        subject = 'TICKET SALE ALERT - '+eventName
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [organizerEmail]
        html_message = render_to_string('static/common/new_sales_to_organizers.html', {
            'event_name': eventName,
            'revenue': amountPaid,
            'sold': ticketSoldQty,
            'name': attendeeName,
            'contactnumber': attendeeContactNumber,
            'email': attendeeEmail,
            'booking_id': bookingId,
            'ticket_name': ticketName
        })

        msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': attendeeEmail})
        msg.content_subtype = "html"
        msg.send(fail_silently=False)
        # ends here ~ send email to organizer

        messageData = {'message':'Successfully Send Confirmation Message to Organizer','responseType':'success', 'messageType':'success'}
        return HttpResponse(json.dumps(messageData))

    except Exception as e:
        print('error while sending email >> ',e)
        messageData = {'message':'Error while Sending Email','responseType':'success', 'messageType':'error'}
        return HttpResponse(json.dumps(messageData))

# @author Shubham ~ Send Confirmation Email to Organizer ~ October 12 2019

# @author Shubham ~ Send Confirmation Email to Organizer ~ October 12 2019
@csrf_exempt
def update_ticket_url(request):
    try:
        ticketUrl = request.POST['ticketUrl']
        eventId = request.POST['eventId']

        # filter and update ticket url in articles2 table
        filterEventData = Articles2.objects.filter(id=eventId).update(ticket_url=ticketUrl)
        # ends here ~ filter and update ticket url in articles2 table

        updated_urls_list = []
        shor_url_objects = ShortUrlTracker.objects.filter(event_id=eventId)
        for short_url_obj in shor_url_objects:
            each_data = {}
            source = short_url_obj.source
            if '/organic/' in ticketUrl.lower():
                if source == 'organic':
                    original_url = ticketUrl
                else: 
                    original_url = re.sub('/organic/', '/'+source+'/', ticketUrl, flags=re.I)
            else:
                original_url = ticketUrl
            short_url_obj.original_url = original_url
            short_url_obj.save()

            each_data['id'] = short_url_obj.id
            each_data['url'] = original_url
            updated_urls_list.append(each_data)

        messageData = {'message':'Update Ticket URL Successfully','responseType':'success', 'messageType':'success','updated_urls_list':updated_urls_list}
        return HttpResponse(json.dumps(messageData))

    except Exception as e:
        print('error while updating ticket url >> ',e)
        messageData = {'message':'Error while Updating Ticket URL. Please Try Again.','responseType':'success', 'messageType':'error'}
        return HttpResponse(json.dumps(messageData))

# @author Shubham ~ Send Confirmation Email to Organizer ~ October 12 2019

# @author Shubham ~ Get "what_to_process" list from "event_processes" table ~ October 14 2019
def getEventProcessList():
    try:
        filterEventProcesses = EventProcesses.objects.filter(active=1).values('what_to_process','process_id','msg_to_org')

        filterEventProcList = []
        for data in filterEventProcesses:
            filterEventProcList.append(data)

        return filterEventProcList

    except Exception as e:
        print('error while fetching data from event_processes table >> ',e)
# ends here ~ @author Shubham ~ Get "what_to_process" list from "event_processes" table ~ October 14 2019

# @author Shubham ~ Send Confirmation Email to Organizer ~ October 15 2019
@csrf_exempt
def change_event_status(request):
    try:
        completeReqData = request.POST['completeData']
        completeReqJson = json.loads(completeReqData)

        # data from json dict to eventId 
        eventId = completeReqJson['eventId']
        eventFailedReason = completeReqJson['failed']
        eventPassedReason = completeReqJson['passed']
        eventStatusActionType = completeReqJson['actionType']
        fullname = completeReqJson['user_fullname']
        adminId = request.session['admin_id']
        # ends here ~ data from json dict to eventId

        # fetch city name from articles 2 table
        filterArtiData = Articles2.objects.filter(id=eventId).values('city','event_name')
        articleCityName = list(filterArtiData)[0]['city']
        articleEventName = list(filterArtiData)[0]['event_name']
        # ends here ~ fetch city name from articles 2 table

        # query for filter data from different table to get organizer email
        filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=eventId).values('connected_user')
        connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']

        filterUserData = Users.objects.get(id = connectedUserId)
        organizerEmail = filterUserData.user
        # ends here ~ query for filter data from different table to get organizer email

        # eventVerificationFilter = EventVerificationResult.objects.filter(event_id=eventId)

        EventVerificationResult.objects.filter(event_id=eventId).delete() #delete old data from EventVerificationResult Table


        if eventStatusActionType == 'unapproved':
            # if event status need to change to unapproved or failed OR action type is unapproved 

            # verified against list for db
            # varifiedAgainst = []
            # for eFailedReason in eventFailedReason:
            #     varifiedAgainst.append(eFailedReason['process_id'])
            # varifiedAgainstStr = str(varifiedAgainst)
            # ends here ~ verified against list for db

            # update data to database EventVerificationResult table
            for eFailedReason in eventFailedReason:
                EventVerificationResult.objects.create(event_id=eventId,verified_against=eFailedReason['process_id'],status='fail')
            for ePassedReason in eventPassedReason:
                EventVerificationResult.objects.create(event_id=eventId,verified_against=ePassedReason['process_id'],status='pass')
            # ends here ~ update data to database EventVerificationResult table

            # change status of event (disapproved or 0)
            StatusPromotionTicketing.objects.filter(event_id=eventId).update(approval=0,event_active=5)
            # ends here ~ change status of event (disapproved or 0)

            # send email to organizer
            subject = 'Your event '+articleEventName+' has been disapproved - Ercess Live'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [organizerEmail]
            html_message = render_to_string('static/common/approval_failed.html', {
                'failedReason': eventFailedReason,
                'username': fullname,
                'event_name':articleEventName
            })

            msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
            msg.content_subtype = "html"
            msg.send(fail_silently=False)
            # ends here ~ send email to organizer

        elif eventStatusActionType == 'approved':
            # eventProcessLen = completeReqJson['eventProcessLen']

            # # verified against list for db
            # varifiedAgainst = []
            # for count in range(1,int(eventProcessLen)):
            #     varifiedAgainst.append(count)
            # varifiedAgainstStr = str(varifiedAgainst)
            # # ends here ~ verified against list for db

            # # update data to database EventVerificationResult table 
            # if not eventVerificationFilter:
            #     EventVerificationResult.objects.create(event_id=eventId,verified_against=varifiedAgainstStr,status='pass')
            # else:
            #     EventVerificationResult.objects.filter(event_id=eventId).update(verified_against=varifiedAgainstStr,status='pass')
            # # ends here ~ update data to database EventVerificationResult table 

            # # change status of event (disapproved or 0)
            # StatusPromotionTicketing.objects.filter(event_id=eventId).update(approval=1,event_active=1)
            # # ends here ~ change status of event (disapproved or 0)


            # # send email to organizer
            # subject = 'Your event '+articleEventName+'  is approved - Ercess Live'
            # email_from = settings.EMAIL_HOST_USER
            # recipient_list = [organizerEmail]
            # html_message = render_to_string('static/common/event_approved.html', {
            #     'username': fullname,
            #     'event_name':articleEventName
            # })

            # msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
            # msg.content_subtype = "html"
            # msg.send(fail_silently=False)
            # # ends here ~ send email to organizer

            # # fetch and set category id and topic id
            # filterCategEvents = CategorizedEvents.objects.filter(event_id=eventId).values('category_id','topic_id')
            # categEvents = list(filterCategEvents)[0]
            # catId = categEvents['category_id']
            # topicId = categEvents['topic_id']
            # # ends here ~ fetch and set category id and topic id

            # # fetch all relevent site_id (partner_id) from ErcessPartnersCategories Table
            # filterErcessPartnerCat = ErcessPartnersCategories.objects.filter(ercess_category=catId).values('partner_id')
            # # ends here ~ fetch all relevent site_id (partner_id) from ErcessPartnersCategories Table

            # # update EventStatusOnChannel Table
            # Idx0PartnerId = filterErcessPartnerCat[0]['partner_id']

            # filterEventStatusChannel = EventStatusOnChannel.objects.filter(event_id=eventId, site_id=Idx0PartnerId)
            # if not filterEventStatusChannel:
            #     EventStatusOnChannel.objects.filter(event_id=eventId).delete()
            #     for ercessPartnerCatData in filterErcessPartnerCat:
            #         EventStatusOnChannel.objects.create(event_id=eventId,site_id=ercessPartnerCatData['partner_id'],promotion_status="ready to upload",partner_status="pending",admin_id=adminId)
            # # ends here ~ update EventStatusOnChannel Table

            ##################################################
            ################ NEW CODE ########################
            ##################################################
            # update data to database EventVerificationResult table
            for ePasedReason in eventPassedReason:
                EventVerificationResult.objects.create(event_id=eventId,verified_against=ePasedReason['process_id'],status='pass')
            # ends here ~ update data to database EventVerificationResult table

            # change status of event (disapproved or 0)
            StatusPromotionTicketing.objects.filter(event_id=eventId).update(approval=1,event_active=1)
            # ends here ~ change status of event (disapproved or 0)


            # send email to organizer
            subject = 'Your event '+articleEventName+'  is approved - Ercess Live'
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [organizerEmail]
            html_message = render_to_string('static/common/event_approved.html', {
                'username': fullname,
                'event_name':articleEventName
            })

            msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
            msg.content_subtype = "html"
            msg.send(fail_silently=False)
            # ends here ~ send email to organizer

            # fetch and set category id and topic id
            filterCategEvents = CategorizedEvents.objects.filter(event_id=eventId).values('category_id','topic_id')
            categEvents = list(filterCategEvents)[0]
            catId = categEvents['category_id']
            # ends here ~ fetch and set category id and topic id

            # fetch all row data from partner_sites table (only active_state=1) & related category from filterErcessPartnerCat on basis of category id
            filterPartnerSites = PartnerSites.objects.filter(active_state=1).values('table_id')
            filterErcessPartnerCat = ErcessPartnersCategories.objects.filter(ercess_category=catId).values('partner_id')

            # ends here ~ fetch all row data from partner_sites table (only active_state=1) & related category from filterErcessPartnerCat on basis of category id

            # fetch required site id
            partnerSiteList = list(map(lambda x : int(x['table_id']), list(filterPartnerSites)))
            ercessPartnerCatList = list(map(lambda x : int(x['partner_id']), list(filterErcessPartnerCat)))
            requiredSiteId = list(set(partnerSiteList) & set(ercessPartnerCatList))
            # ends here ~ fetch required site id

            # update EventStatusOnChannel Table
            Idx0PartnerId = requiredSiteId[0]

            filterEventStatusChannel = EventStatusOnChannel.objects.filter(event_id=eventId, site_id=Idx0PartnerId)
            if not filterEventStatusChannel:
                EventStatusOnChannel.objects.filter(event_id=eventId).delete()
                for ercessPartnerCatData in requiredSiteId:
                    EventStatusOnChannel.objects.create(event_id=eventId,site_id=ercessPartnerCatData,promotion_status="ready to upload",partner_status="pending",admin_id=adminId)
            # ends here ~ update EventStatusOnChannel Table
            

        messageData = {'message':'Action Successfully Performed','responseType':'success', 'messageType':'success'}
        return HttpResponse(json.dumps(messageData))

    except Exception as e:
        print('error while sending email >> ',e)
        messageData = {'message':'Error while Performing required (Approved/Disapproved) Action','responseType':'success', 'messageType':'error'}
        return HttpResponse(json.dumps(messageData))

# @author Shubham ~ Send Confirmation Email to Organizer ~ October 12 2019

# @author Shubham ~ Function for Get Bank Details from DB and return a list 
def getBankDetails(eventIdPar):
    try:
        # query for filter data from different table to get organizer id
        filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=eventIdPar).values('connected_user')
        connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']
        # ends here ~ query for filter data from different table to get organizer id

        filterBankDetails = BankDetails.objects.filter(user_id=connectedUserId).values()

        if not filterBankDetails:
            return {}
        else:
            filterBankDetailsList = list(filterBankDetails)
            filterBankDetailsDict = filterBankDetailsList[0] 
            return filterBankDetailsDict
    except Exception as e:
        print('error while getting bank details',e)
# ends here ~ @author Shubham ~ Function for Get Bank Details from DB and return a list

# @author Shubham ~ Function for Get Organiser Details from DB and return a list 
def getOrganiserDetails(eventIdPar):
    try:
        # query for filter data from different table to get organizer id
        filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=eventIdPar).values('connected_user')
        connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']
        # ends here ~ query for filter data from different table to get organizer id

        filterUserDetails = Users.objects.filter(id=connectedUserId).values()

        if not filterUserDetails:
            return {}
        else:
            filterUserDetailsList = list(filterUserDetails)
            filterUserDetailsDict = filterUserDetailsList[0] 
            return filterUserDetailsDict
    except Exception as e:
        print('error in getOrganiserDetails function >> ',e)
# ends here ~ @author Shubham ~ Function for Get Organiser Details from DB and return a list

# create leads through csv file
@csrf_exempt
def create_leads_csv(request):
    try:
        if request.method == 'POST':
            # read file and other data
            leadsCsvFile = request.FILES['file']
            event_id = request.POST['event_id']
            # ends here ~ read file and other data

            # read csv file and make column insensitive
            decodedCsvFile = leadsCsvFile.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decodedCsvFile)
            reader.fieldnames = [field.strip().lower() for field in reader.fieldnames]
            # ends here ~ read csv file and make column insensitive

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

            duplicateRecords = 0
            successfulAddedRecords = 0
            failedRecords = 0
            currentRow = 1
            failedRowList = []
            # for loop in leads csv file data
            
            for row in reader:
                attendee_name = row['name']
                attendee_email = row['email']
                attendee_contact = row['mobile']
                currentRow+=1
                try:
                    leadsFilterData = Leads.objects.filter(contact=attendee_contact,city=articleCityName,category=catId)
                    if not leadsFilterData:
                        # save rsvp personal data to additional leads table
                        Leads.objects.create(name=attendee_name,email=attendee_email,contact=attendee_contact,category=catId,
                        user_id=request.session['admin_id'],sub_category=topicId,city=articleCityName)
                        # ends here ~ save rsvp personal data to additional leads table
                        successfulAddedRecords+=1
                    else:
                        duplicateRecords+=1
                except Exception as e:
                    failedRecords+=1
                    failedRowList.append(currentRow)
            # ends here ~ for loop in leads csv file data

            dataDict = {'successfulRecords':successfulAddedRecords,'duplicateRecords':duplicateRecords,'failedRecords':failedRecords,'failedRowList':failedRowList}
            
            # return message to ajax
            messageData = {'message': 'Successfully Add Leads Record to Database','data':dataDict,'responseType': 'success', 'messageType': 'success'}
            return HttpResponse(json.dumps(messageData))
            # ends here ~ return message to ajax

    except Exception as e:
        print('error in create_leads_csv function >> ',e)
        # return message to ajax
        messageData = {'message': 'This csv file is not in proper format.','responseType': 'success', 'messageType': 'error'}
        return HttpResponse(json.dumps(messageData))
        # ends here ~ return message to ajax
# ends here ~ create leads through csv file


### Admin feed back List  #######

class AdminFeedBackList(View):
    template_name = "admin_panel/admin-feedback.html"
    def get(self,request,event_id):
        
        feed_back = ExpectationsFeedbacks.objects.filter(event_id = event_id, feedback_mail_status = "customer replied")
        return render(request,self.template_name,locals())


class AdminExpectationList(View):
    template_name = "admin_panel/admin-expection-list.html"
    def get(self,request,event_id):
        
        feed_back = ExpectationsFeedbacks.objects.filter(event_id = event_id, exp_mail_status ="customer replied")
        return render(request,self.template_name,locals())

# function for add promotion
@csrf_exempt
def addEditPromotionLinks(request, event_id):
    try:
        if request.method == 'POST':
            requestData = request.POST
            requestDataDict = dict(request.POST)

            addEditPromoLinksData = requestDataDict
            
            # set values into required variables
            website_name = addEditPromoLinksData['website_name'][0]
            link = addEditPromoLinksData['link'][0]
            promotion_status = addEditPromoLinksData['promotion_status'][0]
            partner_status = addEditPromoLinksData['partner_status'][0]
            adminId = request.session['admin_id']
            eventId = event_id
            # ends here ~ set values into required variables

            # code modify ~ december 20 2019
            eventStatusFilter = EventStatusOnChannel.objects.filter(event_id=eventId,site_id=website_name)
            if(len(eventStatusFilter) == 0):
                EventStatusOnChannel.objects.create(event_id=eventId,site_id=website_name,promotion_status=promotion_status,partner_status=partner_status,admin_id=adminId,link=link)
            else:
                EventStatusOnChannel.objects.filter(event_id=eventId,site_id=website_name).update(promotion_status=promotion_status,partner_status=partner_status,admin_id=adminId,link=link)
            # ends here ~ code modify ~ december 20 2019

            messageData = {'message': 'Successfully Add Record to Database','data':'','responseType': 'success', 'messageType': 'success'}
            return HttpResponse(json.dumps(messageData))

    except Exception as e:
        print('error in addEditPromotionLinks function >> ',e)
# ends here ~  function for add promotion

#Edit details for admin-panel
# Author : Aniket
class EditDetailView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'edit_detail.html'
    def get_object(self, event_id):
        try:
            return Articles2.objects.get(pk=event_id)
        except Articles2.DoesNotExist:
            raise Http404
    def get(self, request,event_id):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        article = self.get_object(event_id)
        serializer = EditViewSerializer(article)
        country=article.country
        pro_image= article.profile_image
        banner = article.banner
        edit_image = article.editable_image
        images = [pro_image,banner,edit_image]
        #Target Tab----------------------------------------------------------
        s_p_tkt = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
        print(s_p_tkt)
        types=''
        tkt_type=''
        for i in s_p_tkt:
            types = i.private
            tkt_type = i.ticketing
        print(types)
        if types == 0 :
            types = 'public'
        else:
            types = 'private'
        if tkt_type == 0:
            tkt_type = 'free'
        else:
            tkt_type = 'paid'
        print(types)
        print(tkt_type)
        cat_event = CategorizedEvents.objects.all().filter(event_id = event_id)
        print(cat_event)
        cat_id = 0
        top_id = 0
        if cat_event.count():
            cat_id = cat_event[0].category_id
        if cat_event.count():
            top_id = cat_event[0].topic_id
        topic = Topics.objects.all().filter(topics_id = top_id)
        category = Categories.objects.all().filter(category_id = cat_id)
        cat = ''
        if len(category)!=0:
            main_category = category[0].category
            print(main_category)
            sub_category=''
            if len(topic)!=0:
                sub_category = topic[0].topic
            elif len(topic)==0:
                sub_category = " "
            print(sub_category)
            cat = (main_category,sub_category)
        #Tickets Tab--------------------------------------------------------
        free =False
        if s_p_tkt[0].ticketing == 0:
            free = True
        tkts = Tickets.objects.all().filter(event_id = event_id)
        print(tkts)
        tkt_name = []
        tkt_price = []
        oth_chrgs = []
        oth_chrgs_type =[]
        tkt_qty = []
        min_qty = []
        max_qty = []
        tkt_left = []
        tkt_msg = []
        s_date = []
        e_date = []
        e_fee = []
        trans_fee = []
        tkt_lbl = []
        activ = []
        for i in tkts:
            tkt_name.append(i.ticket_name)
            tkt_price.append(i.ticket_price)
            oth_chrgs.append(i.other_charges)
            oth_chrgs_type.append(i.other_charges_type)
            tkt_qty.append(i.ticket_qty)
            min_qty.append(i.min_qty)
            max_qty.append(i.max_qty)
            tkt_left.append(i.qty_left)
            tkt_msg.append(i.ticket_msg)
            s_date.append(i.ticket_start_date)
            e_date.append(i.expiry_date)
            e_fee.append(i.ercess_fee)
            trans_fee.append(i.transaction_fee)
            tkt_lbl.append(i.ticket_label)
            activ.append(i.active)
        print(oth_chrgs)
        print("message-------------")
        print(tkt_msg)
        msg1=[]
        for i in tkt_msg:
            if (i == None or i == "" or i =="None" or i == "NULL" or i == "none"):
                msg1.append(0)
            else:
                msg1.append(i)
        print(msg1)
        print("message code------------------ends")
        oth_chrgs2=[]
        for i in oth_chrgs:
            if i == '':
                oth_chrgs2.append(0)
            else:
                oth_chrgs2.append(i)
        print(oth_chrgs2)
        print(oth_chrgs_type)
        oth_chrgs_type2=[]
        for i in oth_chrgs_type:
            if i == 0:
                oth_chrgs_type2.append(0)
            elif i == 1:
                oth_chrgs_type2.append(1)
            elif i == 2 :
                oth_chrgs_type2.append(2)
        print(oth_chrgs_type2)
        print(activ)
        activ2=[]
        for i in activ:
            if i == 0:
                activ2.append('inactive')
            elif i == 1:
                activ2.append('active')
            elif i == 2:
                activ2.append("deleted")
        print(activ2)
        print(country)
        currency = AboutCountries.objects.all().filter(country= country).values('currency')
        print(currency)
        if currency.count() > 0:
            currency = currency[0]['currency']
        print(currency)
        print("Question tab---------------------------")
        # Question Tab
        builder = AttendeeFormBuilder.objects.all().filter(event_id=event_id)
        print(builder)
        title = []
        mand = []
        q_type = []
        q_id = []
        if len(builder) != 0:
            for i in builder:
                title.append(i.ques_title)
                mand.append(i.ques_accessibility)
                q_type.append(i.ques_type)
                q_id.append(i.ques_id)
        print(title)
        print(mand)
        name = []
        type_id = []
        for i in q_type:
            form_type = AttendeeFormTypes.objects.all().filter(type_id=i)
            name.append(form_type[0].name)
            type_id.append(form_type[0].type_id)
        print(name)
        optn_name = []
        for i in q_id:
            form_option = AttendeeFormOptions.objects.all().filter(ques_id=i)
            if len(form_option) != 0:
                if form_option[0].event_id == event_id:
                    optn_name.append(form_option[0].option_name)
                else:
                    optn_name.append(" ")
            else:
                optn_name.append(" ")
        print(optn_name)
        x = zip(title, mand, name, optn_name)
        items = zip(tkt_name, tkt_price, oth_chrgs2,
                    oth_chrgs_type2, tkt_qty, min_qty,
                    max_qty, tkt_left, msg1, s_date, e_date,
                    e_fee, trans_fee, tkt_lbl, activ2)
        return Response({'article': article,'cat':cat,'images':images,
                         'types':types ,'currency':currency,'free':free,
                         'tkt_type':tkt_type,'items':items,'x':x})