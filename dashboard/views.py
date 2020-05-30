import json
from django.shortcuts import render , redirect
from .forms import HowForm, ChangePasswordForm 
from Ercesscorp.models import RegistrationData, Users
#from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import  AttendeeFormBuilder,AttendeeFormOptions,AttendeeFormTypes,Articles2, Tickets,AboutCountries ,StatusPromotionTicketing ,TicketsSale,Categories,CategorizedEvents,Topics, ExpectationsFeedbacks # , Photo
# from .models import Photo
#from .forms import PhotoForm
from html.parser import HTMLParser
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime,timedelta
from io import  StringIO
from django.core.files.base import ContentFile
import  os
from django.conf import settings
from hashlib import md5
from django.http import  JsonResponse, HttpResponse, HttpResponseRedirect
from .forms import HowForm, ChangePasswordForm,UpdateUser
from Ercesscorp.third_party_security import smartlogin
from .models import Articles2, StatusPromotionTicketing, Rsvp, PaymentSettlement ,BankDetails, Announcements, AnnouncementsAccess, Leads  #, Photo
from Ercesscorp.models import RegistrationData, Users
from django.utils import timezone
# from .models import Photo
#from .forms import PhotoForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework import status
from django.views.generic import View
#this is new
from .serializers import EditViewSerializer,EditTicketSerializer
from rest_framework import viewsets
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib import messages
import csv, io
import re 
import uuid
from django.core.files.base import ContentFile

email_sent_from = settings.EMAIL_HOST_USER



def getHow(request):
    try:
        # print('inside get how')
        sub = request.session.get('sub')
        currencySymbol=''
       
        # print(sub)
        if sub == 0:
            sub = False
        elif sub == 1:
            sub = True
        uname = request.session.get('username')
        # print('in views of dash')
        # print(uname)
        if 'userid' not in request.session.keys():
            return redirect('/live/login')

        # new code for announcement
        loginUserId = request.session['userid']
        announcementFilter = Announcements.objects.filter(status='active').values('ann_id','dashboard_msg')
        announcementList = list(announcementFilter)
        finalAnnouncementList = []

        for announcement in announcementList:
            announcementFilter = AnnouncementsAccess.objects.filter(user_id=loginUserId, announcement_id=announcement['ann_id'])
            if not announcementFilter:
                finalAnnouncementList.append(announcement)

        print(finalAnnouncementList)
        # ends here ~ new code for announcement

        # analytics
        ################################################

        # required variables
        userId = request.session.get('userid')
        currentDateTime = datetime.now()
        # ends here ~ required variables

        # get all event_id of events according to connected_user (or current login user) 
        statusPromoFilter = StatusPromotionTicketing.objects.filter(connected_user=userId, complete_details=1).order_by('-status_promotion_ticketing_id').values('event_id')
        statusPromoList = list(statusPromoFilter)
        # ends here ~ get all event_id of events according to connected_user (or current login user) 

        ##########################################################
        # FOR UPCOMING EVENTS
        ##############################
        
        # upcoming event list
        upcomingEventsList = []
        for statusPromoData in statusPromoList:
            eventId = statusPromoData['event_id']
            # filter event_id
            articles2Filter = Articles2.objects.filter(edate__gte=currentDateTime, id=eventId).order_by('-id').values()
            if(len(articles2Filter) > 0):
                articles2Dict = list(articles2Filter)[0]
                upcomingEventsList.append(articles2Dict.copy())
            # ends here ~ filter event_id
        # ends here ~ upcoming event list

        # filter ticket sales data
        upcomingEventSalesList = []
        lastFewticketSalesList = []
        totalUpcomingEventSalesAmt = 0
        totalUpcomingEventSalesCount = 0
        totalUpcomingSalesTktQty = 0
        totalUpcomingEventCount = len(upcomingEventsList)
        for eventData in upcomingEventsList:
            lastFewticketSalesDict = {'buyer_name':'','ticket_qty':'','sales_amt':'','purchase_datetime':'','mobile':'','email':'','table_id':''}
            eventId = eventData['id']

            # get currency
            eventCountry = eventData['country']
            aboutCountriesFilter = AboutCountries.objects.filter(country=eventCountry).values()
            if(len(aboutCountriesFilter) > 0):
                aboutCountriesList = list(aboutCountriesFilter)
                aboutCountriesDict = aboutCountriesList[0]
                currencySymbol = aboutCountriesDict['currency']
            else:
                currencySymbol = ''
            # ends here ~ get currency

            eventName = eventData['event_name']
            # ticketSalesFilter = TicketsSale.objects.filter(event_id=eventId).order_by('-table_id').values()
            ticketSalesFilter = TicketsSale.objects.filter(event_id=eventId).order_by('-table_id').values()
            totalSales = len(ticketSalesFilter)

            # get total amount of upcoming events and its sales
            # totalUpcomingEventSalesCount = totalSales
            totalUpcomingEventSalesCount+= totalSales            
            currentTicketTotalSalesAmt = 0
            if(totalSales > 0):
                ticketSalesList = list(ticketSalesFilter)
                for ticketData in ticketSalesList:
                    totalUpcomingEventSalesAmt+=ticketData['ampunt_paid']
                    currentTicketTotalSalesAmt+=ticketData['ampunt_paid']
                    totalUpcomingSalesTktQty+= ticketData['qty']
                    # append sales details to lastFewticketSalesList (to show last 5 details)
                    if(len(lastFewticketSalesList) < 6):
                        lastFewticketSalesDict['buyer_name'] = ticketData['attendee_name']
                        lastFewticketSalesDict['ticket_qty'] = ticketData['qty']
                        lastFewticketSalesDict['table_id'] = ticketData['table_id']
                        lastFewticketSalesDict['sales_amt'] = ticketData['ampunt_paid']
                        lastFewticketSalesDict['purchase_datetime'] = ticketData['purchase_date']
                        lastFewticketSalesDict['mobile'] = ticketData['attendee_contact']
                        lastFewticketSalesDict['email'] = ticketData['attendee_email']

                        lastFewticketSalesList.append(lastFewticketSalesDict.copy())
                    # ends here ~ append sales details to lastFewticketSalesList
            # ends here ~ get total amount of upcoming events and its sales

            upcomingEventSalesList.append([eventName,currentTicketTotalSalesAmt, currencySymbol])
            # upcomingEventSalesList.append(salesUpcomingEventDict.copy())
        # ends here ~ filter ticket sales data

        #####################################
        # ENDS HERE ~ FOR UPCOMING EVENTS
        #########################################################

        ##########################################################
        # FOR LIFETIME EVENTS
        #####################################

        # lifetime event list
        lifetimeEventsList = []
        # for statusPromoData in statusPromoList:
        #     eventId = statusPromoData['event_id']
        #     # filter event_id
        #     articles2Filter = Articles2.objects.filter(id=eventId).values()
        #     if(len(articles2Filter) > 0):
        #         articles2Dict = list(articles2Filter)[0]
        #         lifetimeEventsList.append(articles2Dict.copy())
            # ends here ~ filter event_id
        # ends here ~ lifetime event list

        # filter ticket sales data
        totalLifetimeEventSalesCount = 0
        totalLifetimeSalesTktQty = 0
        totalLifetimeEventCount = len(lifetimeEventsList)
        totalLifetimeSalesAmt = 0 
        # for eventData in lifetimeEventsList:
        #     eventId = eventData['id']
        #     ticketSalesFilter = TicketsSale.objects.filter(event_id=eventId).values()
        #     totalSales = len(ticketSalesFilter)
        #     totalLifetimeEventSalesCount+=totalSales

        #     if(totalSales > 0):
        #         ticketSalesList = list(ticketSalesFilter)
        #         for ticketData in ticketSalesList:
        #             totalLifetimeSalesTktQty+= ticketData['qty']
        #             totalLifetimeSalesAmt+=ticketData['ampunt_paid']

        # ends here ~ filter ticket sales data

        # new code
        ticketSalesFilter = TicketsSale.objects.filter(oragnizer=userId).values()
        lifetimeEventsList = list(ticketSalesFilter)

        totalLifetimeEventSalesCount = len(lifetimeEventsList)
        totalLifetimeEventCount = len(statusPromoList)
        # len(list({v['event_id']:v for v in lifetimeEventsList}.values()))

        for ticketData in lifetimeEventsList:
            totalLifetimeSalesTktQty+= ticketData['qty']
            totalLifetimeSalesAmt+=ticketData['ampunt_paid']
        # ends here ~ new code 

        #####################################
        # ENDS HERE ~ FOR LIFETIME EVENTS
        #########################################################

        ################################################
        # ends here ~ analytics

        # filter contact number from users table
        userFilter = Users.objects.get(id=userId)
        mobileNumber = userFilter.mobile
        # ends here ~ filter contact number from users table

        if request.method == 'POST':
            form = HowForm(request.POST)
            if form :
                how = request.POST.get('choices', '')
                other = request.POST.get('other', '')
                x = User.objects.get(username=uname)
                # print('in dash views')
                # print(x.pk)
                if x :
                    r = RegistrationData.objects.get(user_id = x.pk)
                    print(r)
                    r.submitted = 1
                    if how != 'others' :
                        r.how_u_know = how
                    else :
                        r.how_u_know = other
                    r.save()
                    # return  redirect('dashboard:home')
                    sub = True
            form = HowForm()
            return render(request, 'gethow.html', {'sub': sub, 'form': form})
        else :
            form = HowForm()
            # print('sub'+str(sub))

            lastFewticketSalesList = sorted(lastFewticketSalesList, key=lambda k: k['table_id'], reverse=True)
            return render(request , 'gethow.html' ,{'sub':sub ,'form':form, 'announcement_list':finalAnnouncementList, 'upcoming_event_sales_list':upcomingEventSalesList,'total_upcoming_evt_sales_amt':totalUpcomingEventSalesAmt,'total_upcoming_evt_sales_count':totalUpcomingEventSalesCount,'total_lifetime_evt_count':totalLifetimeEventCount,'total_lifetime_evt_sales_count':totalLifetimeEventSalesCount,'last_few_ticket_sales_list':lastFewticketSalesList,'total_upcoming_sales_tkt_qty':totalUpcomingSalesTktQty,'total_upcoming_event_count':totalUpcomingEventCount,'total_lifetime_sales_tkt_qty':totalLifetimeSalesTktQty,'total_lifetime_sales_amt':totalLifetimeSalesAmt,'mobile_number':mobileNumber, 'currencySymbol':currencySymbol})

    except Exception as e:
        username = request.session.get('userid')
        print('error in getHow fn >> ',e)

        return HttpResponseRedirect('/live/dashboard/')



###### update user informations ###########
class UpdateUserInfo(View):
    
    def get(self,request):
        user_id = request.session.get('userid')
        user = Users.objects.get(id = user_id)
        f_name = user.firstname 
        l_name = user.lastname
        email = user.user
        mobile = user.mobile
        img = user.profile_pic
        print(img,'============')
        organization_name = user.organization_name
        
        form1 = UpdateUser()
        return render(request, 'update-user-profile.html', {'form1':form1,'f_name':f_name,'l_name':l_name,'email':email,'mobile':mobile, 'organization_name':organization_name, 'img':img})

    def post(self,request):
        user_id = request.session.get('userid')
        user = Users.objects.get(id = user_id)
        f_name = request.POST.get('firstname')
        l_name = request.POST.get('lastname')
        mobile = request.POST.get('mobile')
        organization_name = request.POST.get('Organization_name')
        profile_image = request.FILES.get('Image')
        print(profile_image,'>>>>>>>>>>>')
        
        if profile_image:
            image_name = (profile_image.name).strip()
            try:
                Users.objects.get(profile_pic = image_name)
                random_string = str(uuid.uuid4())[:8]
                image_name = random_string + '_' + image_name
            except Users.DoesNotExist:
                pass
            profile_pic = settings.MEDIA_URL + image_name

            try:
               
                print(profile_pic)
                full_path =  settings.MEDIA_DIR + '/' + image_name
                print(full_path)
                print(profile_pic)
                fout = open(full_path, 'wb+')

                file_content = ContentFile(profile_image.read())
                for chunk in file_content.chunks():
                    
                    fout.write(chunk)
                fout.close()
                user.firstname = f_name
                user.lastname = l_name
                user.mobile = mobile
                user.organization_name = organization_name
                user.profile_pic = profile_pic
                user.save()
            except Exception as e:
                raise e
        else:
            img = user.profile_pic
            user.firstname = f_name
            user.lastname = l_name
            user.mobile = mobile
            user.organization_name = organization_name
            user.profile_pic = img
            user.save()
        
        
        return HttpResponseRedirect('/live/dashboard/update_info')
''' 

def third_step(request , eventid):
    pic1 = pic2 = None
    x = ''
    ft = fe = fi = 0
    didnt_recognize = False
    error_upload = False
    upload_size_error = False
    user = None
    try:
        user = Articles2.objects.get(id=eventid)
    except:
        user = None
        print('inside except third step ')
    else :
        pic1 = user.company_logo
        pic2 = user.event_banner
    if request.method == 'POST' :
        if user is not None:
            try :
                i = float(request.POST.get('x'))
                j = float(request.POST.get('y'))
                height = float(request.POST.get('height'))
                width = float(request.POST.get('width'))
                print(type(i), type(j), type(width), type(height))
            except:pass

            try:
                iname = image = request.FILES['thumbnail']
                print(image.size)
                user.company_logo = thumbnail(image ,iname ,i,j, width,height)
                print('saved')
            except Exception as e:
                ft = 1
                print('thumbnail')
                print(e)
            else :x = user.save()
            try :
                iname = image = request.FILES['eventbanner']
                if image.size >5242880 :
                    return redirect('/live/dashboard/create-event/step-three/'+ eventid +'?upload_size_error=True')
                else:
                    user.event_banner = passer(image, iname, i,j, width,height)
                    print('saved')
                # user.event_banner = passer(user.event_banner.file, i, j, width, height)
            except :
                fe = 1
                print('eventbanner')
            else : x = user.save()

            try:
                user.editable_image = request.FILES['editableimage']
                #have to send mail to ercess
            except :
                fi  = 1
                print('editableimage')
            else :x = user.save()
            if x is None :
                print('inside else if ')
                return redirect('/live/dashboard/create-event/step-three/'+ eventid)
            else :
                return redirect('/live/dashboard/create-event/step-three/'+ eventid +'?error_upload=True')
        else :
            return redirect('/live/dashboard/create-event/step-three/'+ eventid +'?didnt_recognize=True')
    else :
        pic1 = user.company_logo
        pic2 = user.event_banner
        if 'error_upload' in request.GET:
            error_upload = True
        if 'didnt_recognize' in request.GET:
            didnt_recognize = True
        if 'upload_size_error' in request.GET:
            upload_size_error = True
        return render(request , 'step_three.html',{'error_upload':error_upload,
                                                   'didnt_recognize':didnt_recognize,
                                                   'pic1':pic1 ,'pic2':pic2 , 'upload_size_error':upload_size_error})
'''
'''
def photo_list(request):
    photos = Photo.objects.all()
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        print(form)
        if form.is_valid():
            print(form.save())
            return redirect('/live/dashboard/test')
    else:
        form = PhotoForm()
    return render(request, 'photo_list.html', {'form': form, 'photos': photos})
'''

def passer(image,iname, x , y , w , h):
    image = Image.open(image)
    print(image)
    box = (x, y, w + x, h + y)
    cropped_image = image.crop(box)
    print(cropped_image)
    resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
    print(resized_image)
    resized_image.save(r'media\third_step_images\e' + str(iname))
    return  str(r'third_step_images\e')+str(iname)


def thumbnail(image,iname, x , y , w , h):
    image = Image.open(image)
    print(image)
    box = (x, y, w + x, h + y)
    cropped_image = image.crop(box)
    print(cropped_image)
    resized_image = cropped_image.resize((100, 100), Image.ANTIALIAS)
    print(resized_image)
    # resized_image.save(r'media\third_step_images\e' + str(iname))
    # x = str(iname).split('.')
    resized_image.save(r'media\third_step_images\e'+str(iname), "JPEG",quality=100)
    return  str(r'third_step_images\e')+str(iname)


@csrf_exempt
def change_password(request):
    print('inside view')
    if request.method == 'POST':
        print('post')
        requestData = request.body
        requestDataDecode = requestData.decode('utf8').replace("'", '"')
        requestDataJson = json.loads(requestDataDecode)
        print(requestDataJson)
        userpassword = requestDataJson['oldpass']
        newpassword = requestDataJson['newpass']

        #form = ChangePasswordForm(request.POST)
        #if form.is_valid():
        flag=False
        success=False
        exe = False
        #newpassword = form.cleaned_data['newpassword1']
         #   userpassword = form.cleaned_data['oldpassword']
        username = request.session.get('username')
        print(username)
        x = Users.objects.get(user=username)
        print(x)
        email = x.user
        password = x.password
        pswd_encoded = md5(userpassword.encode('utf-8')).hexdigest()
        print(Users.objects.filter(user=email, password=pswd_encoded).exists())
        if Users.objects.filter(user=email, password=pswd_encoded).exists():
                user = Users.objects.get(user=email, password=pswd_encoded)
                new_pswd_encoded = md5(newpassword.encode('utf-8')).hexdigest()
                user.password = new_pswd_encoded
                user.save()
                try:
                    # send_mail('Password Changed','You have successfully changed your password.',email_sent_from,[email,])
                    # @author Shubham ~ Send Email on reset password ~ october 12 2019
                    subject = 'Your Ercess Live account password has been updated'
                    email_from = settings.EMAIL_HOST_USER
                    recipient_list = [email]

                    html_message = render_to_string('static/common/password_update_template.html')

                    msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
                    msg.content_subtype = "html"
                    msg.send(fail_silently=False)
                    # ends here ~ @author Shubham ~ Send Email on reset password ~ october 12 2019
                    print('in try')
                    #clear_list()
                except Exception as e:
                    print(e)
                    messageData = {'message':'Unexpected Error occured. Try again later !','responseType':'success', 'messageType':'error'}
                    return HttpResponse(json.dumps(messageData))
                    #return render(request, 'settings.html',{'error':e,'exe':exe,'form': form})
                print('done')
                messageData = {'message':'Password changed successfully !','responseType':'success', 'messageType':'success'}
                return HttpResponse(json.dumps(messageData))
                #return render(request, 'settings.html',{'success':success,'form': form})

        else:
            print('wrong')
            messageData = {'message':'Incorrect Old Password','responseType':'success', 'messageType':'error'}
            return HttpResponse(json.dumps(messageData))
            #return render(request, 'settings.html',{'error':'You have entered wrong old password','flag':flag,'form': form})


    else:
        form = ChangePasswordForm()
    return render(request, 'settings.html',{'form': form})

# class EditView(viewsets.ModelViewSet):
#     queryset = Articles2.objects.all()
#     serializer_class = EditViewSerializer


def RSVPlist(request):
    user_id = request.session.get('userid')
    print(user_id)
    q1=StatusPromotionTicketing.objects.get(connected_user=user_id)

    print(q1)
    # event_status_id = event_status_id
    # if event_status_id:
    #     status_obj = EventStatus.objects.get(status_id = event_status_id)
    
    #     status_name = status_obj.name
    #     event_status.append(status_name)
    # else:
    #      event_status.append('not available ')
    q2=Articles2.objects.filter(id=36663)#q1.event_id)
    print(q2)
    rsvp_count={}
    for i in q2:
        rsvp_count[q2.id]=rsvp.objects.filter(event_id=q2.event_id).count()
    return render(request,'RSVP.html',{'entries1':q2},{'rsvp_count':rsvp_count})


class EditView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'edit_list.html'
    def get(self, request):
        queryset = Articles2.objects.all()

        return Response({'Articles': queryset})

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


    # def put(self, request, pk, format=None):
    #     article = self.get_object(pk)
    #     serializer = EditViewSerializer(article, data=request.data)
    #     if not serializer.is_valid():
    #         return Response({'serializer': serializer, 'article': article})
    #     serializer.save()
    #     return redirect('article-list')

    # def delete(self, request, pk, format=None):
    #     article = self.get_object(pk)
    #     article.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)



class ExpectationList(View):
    template_name = "ExpectationList.html"
    def get(self,request,event_id):
        event = Articles2.objects.get(id = event_id)
        print(event,'>>>>>>>>>>>>>>>>>>')
        expectation = ExpectationsFeedbacks.objects.filter(event_id = event_id, exp_mail_status ="customer replied")

        return render(request,self.template_name,locals())


# FeedBAck List 
class FeedBackList(View):
    template_name = "feedback-list.html"
    def get(self,request,event_id):
        event = Articles2.objects.get(id = event_id)
        feed_back = ExpectationsFeedbacks.objects.filter(event_id = event_id, feedback_mail_status = "customer replied")

        return render(request,self.template_name,locals())



# Upload feedback  CSV File 
class UploadCSV(View):
    template_name = "upload-csv.html"
    def get(self,request,event_id):

        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        user_id = request.session.get('userid')
        return render(request, self.template_name,locals())

    def post(self,request,event_id):
        response = {}
        print(request.POST)
        cate = CategorizedEvents.objects.get(event_id = event_id)
        article = Articles2.objects.get(id = event_id)
        city = article.city
        topicId = cate.topic_id
        category = cate.category_id
        regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        user_id = request.session.get('userid')
        csv_file = request.FILES.get('file')
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'THIS IS NOT A CSV FILE')
        
        else:
            duplicate_email = 0
            faild_email = 0
            added_emails = 0

            decode_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decode_file)
            for data in reader:
                all_email = data['Email']
                number = data['Mobile']
                name = data['Name']
                numberRegex=re.compile('^[0-9]{10}$')
                numberValid = numberRegex.match(number)
                if(re.search(regex,all_email)) and numberValid:
                
                    emails = Leads.objects.filter(email = all_email, contact=number,city=city,category=category)  
                  
                    for i in emails:
                        duplicate_email+=1
                        response['status'] = True 
                        response['duplicate_length'] = duplicate_email
                    if not emails:
                        added_email = all_email

                        lead = Leads.objects.create(name=name, email = all_email,contact = int(number),sub_category=topicId,  category = int(category), user_id = int(user_id), city = city)
                        event = ExpectationsFeedbacks.objects.get_or_create(
                                event_id = event_id,
                                uploaded_by = user_id,
                                provided_for = 'expectation',               
                                )
                        
                        added_emails+=1
                        response['status'] = True 
                        response['add_email_length'] = added_emails
                else:
                    faild_email+=1 
                    response['status'] = True 
                    response['faild_emails'] = faild_email
                    
        return HttpResponse(json.dumps(response), content_type = 'application/json')

       
