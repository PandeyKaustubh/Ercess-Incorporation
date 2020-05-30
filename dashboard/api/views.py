from hashlib import md5
from django.shortcuts import redirect, get_object_or_404, render
from django.http import HttpResponse
from django.contrib import messages
from django.core import serializers
from django.urls import reverse
from urllib.parse import urlencode

from django.views.generic import TemplateView
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.renderers import TemplateHTMLRenderer, StaticHTMLRenderer
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.response import Response
from datetime import datetime
import json
from django.conf import settings
from django.core.mail import  send_mail
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from rest_framework.views import APIView

from dashboard.api.serializers import StallSerializer, FacilitiesSerializer, StallUploadSerializer
from dashboard.models import (Articles2, Categories, Topics, StatusPromotionTicketing,
                              AttendeeFormTypes, AttendeeFormOptions, AttendeeFormBuilder,
                              Tickets, AboutCountries, BankDetails, FinanceStandardCharges, TicketDiscounts,
                              ErcessOffers, Stall, StallsProducts, StallsAudience, CategoriesStalls, StallAudience,
                              StallFacilities, StallUpload)
from dashboard.forms import Articles2Form, StallUploadForm
from .serializers import (Articles2Serializer, CategorizedEventsSerializer,
                         StatusPromotionTicketingSerializer, TicketsSerializer,
                          BankDetailsSerializer)


from Ercesscorp.models import Users
from django.views.decorators.csrf import csrf_exempt
import uuid

from dashboard import url_shortner

class EventSuccessView(TemplateView):
    def get(self, request, event_id, *args, **kwargs):

        return render(request, template_name='dashboard/event_success.html', context={'event_id': event_id})


class StallUploadUpdateAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'stall/upload_update.html'
    parser_classes = (MultiPartParser, FormParser)
    def get(self, request, event_id, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        uploads = get_object_or_404(StallUpload, event_id=event_id)
        serializer = StallUploadSerializer(uploads)
        print(uploads.img.url)
        return Response({'serializer': serializer, 'event_id':event_id, 'uploads':uploads})
    def post(self, request, event_id, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        uploads = get_object_or_404(StallUpload, event_id=event_id)
        serializer = StallUploadSerializer(uploads, data=request.data)
        if not serializer.is_valid():
            serializer_error = True
            return Response({'serializer': serializer,
                             'serializer_error': serializer_error,
                             'uploads':uploads,
                             'event_id':event_id})
        # event_id = request.session.get('event_id')
        serializer.save(event_id=event_id)
        return redirect('dashboard:stall_update', event_id=event_id)

class StallUploadAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'stall/step_2/upload.html'
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, event_id, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')

        serializer = StallUploadSerializer

        return Response({'serializer': serializer, 'event_id':event_id})


    def post(self, request, event_id, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')

        serializer = StallUploadSerializer(data=request.data)

        if not serializer.is_valid():
            serializer_error = True
            return Response({'serializer': serializer, 'serializer_error': serializer_error, 'event_id':event_id})

        # event_id = request.session.get('event_id')

        serializer.save(event_id=event_id)

        return redirect('dashboard:create_stall', event_id=event_id)


class FacilitiesAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'stall/step_1/facilities.html'
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, event_id, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        print(request.session.get('event_id'))
        serializer = FacilitiesSerializer
        accepted_product = CategoriesStalls.objects.all()
        audience_type = StallAudience.objects.all()

        return Response({'serializer': serializer,
                         'accepted_product': accepted_product,
                         'audience_type': audience_type,
                         'event_id':event_id
                         })

    def post(self, request, event_id):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        serializer = FacilitiesSerializer(data=request.data)
        accepted_product = CategoriesStalls.objects.all()
        audience_type = StallAudience.objects.all()

        if not serializer.is_valid():
            serializer_error = True
            return Response({'serializer': serializer,
                             'serializer_error': serializer_error,
                             'event_id':event_id,
                             'accepted_product': accepted_product,
                             'audience_type': audience_type,
                             })
        data = dict(request.data)
        request.session['accepted_products'] = data.get('accepted_product')
        request.session['audience_types'] = data.get('type_of_audience')

        # event_id = request.session.get('event_id')

        serializer.save(event_id=event_id)
        return redirect('dashboard:stall_upload', event_id=event_id)


class FacilitiesUpdate(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'stall/facilities_update.html'
    def get(self, request, event_id, *args, **kwargs):
        # if 'userid' not in request.session.keys():
        #     return redirect('/live/login')
        facilities = get_object_or_404(StallFacilities, event_id=event_id)
        selected_prod = facilities.accepted_product.all().values_list('table_id', flat=True)
        selected_aud = facilities.type_of_audience.all().values_list('table_id', flat=True)
        print(facilities.expected_footfall, list(selected_prod))
        serializer = FacilitiesSerializer(facilities)
        accepted_product = CategoriesStalls.objects.all()
        audience_type = StallAudience.objects.all()
        return Response({'serializer': serializer,
                         'accepted_product': accepted_product,
                         'audience_type': audience_type,
                         'event_id': event_id,
                         'facilities': facilities,
                         'selected_prod': selected_prod,
                         'selected_aud': selected_aud
                         })
    def post(self, request, event_id, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        facilities = get_object_or_404(StallFacilities, event_id=event_id)
        serializer = FacilitiesSerializer(facilities, data=request.data)
        selected_prod = facilities.accepted_product.all().values_list('table_id', flat=True)
        selected_aud = facilities.type_of_audience.all().values_list('table_id', flat=True)
        accepted_product = CategoriesStalls.objects.all()
        audience_type = StallAudience.objects.all()
        if not serializer.is_valid():
            serializer_error = True
            return Response({'serializer': serializer,
                             'accepted_product': accepted_product,
                             'audience_type': audience_type,
                             'event_id': event_id,
                             'facilities': facilities,
                             'selected_prod': selected_prod,
                             'selected_aud': selected_aud,
                             'serializer_error': serializer_error,
                             })
        serializer.save(event_id=event_id)
        return redirect('dashboard:stall_upload', event_id=event_id)


class StallUpdateAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    template_name = 'stall/stall_update.html'

    def get(self, request, event_id, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        stall = get_object_or_404(Stall, event_id=event_id)
        serializer = StallSerializer(stall)

        return Response({'serializer':serializer,'errorMessage':'', 'stall': stall, 'event_id':event_id})

    def post(self, request, event_id, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')

        stall = get_object_or_404(Stall, event_id=event_id)
        serializer = StallSerializer(stall, data=request.data)

        if not serializer.is_valid():

            serializer_error = True
            return Response({'serializer': serializer,
                             'stall': stall,
                             'serializer_error': serializer_error,
                             'event_id':event_id})


        serializer.save(event_id=event_id)

        return redirect('dashboard:stall_added')


class StallCreateAPIView(APIView):
    renderer_classes = [TemplateHTMLRenderer]

    template_name = 'stall/stall_create.html'

    def get(self, request, event_id, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        serializer = StallSerializer

        return Response({'serializer':serializer,'errorMessage':'', 'event_id':event_id})

    def post(self, request, event_id, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')

        serializer = StallSerializer(data=request.data)

        if not serializer.is_valid():
            print(serializer.errors)

            serializer_error = True
            return Response({'serializer': serializer, 'serializer_error': serializer_error, 'event_id':event_id})

        stall = serializer.save(event_id=event_id)
        products = request.session.get('accepted_products')
        audiences = request.session.get('audience_types')

        for product in products:
            StallsProducts.objects.create(event_id=event_id,
                                          stall_id=stall.id,
                                          product_id=product)
        for audience in audiences:
            StallsAudience.objects.create(event_id=event_id,
                                          stall_id=stall.event_id,
                                          audience=audience)

        return redirect('dashboard:stall_added')


class ArticlesCreateAPIView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    queryset = Articles2.objects.all()
    serializer_class= Articles2Serializer
    template_name = 'dashboard/create-event/step_1/step_one.html'

    def get(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        #######################contact#########################
        user = Users.objects.get(pk=request.session['userid'])
        print('\n\n\n\n\n\n',user.mobile)
        if user.mobile == '' or user.mobile == 0 :
            return redirect('dashboard:updateContact')

        #######################################################

        return Response({'dashboard': self.queryset, 'serializer':self.serializer_class,'errorMessage':''})


    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')

        # @author Shubham ~ new code to check duplicate and return an error message to UI
        requestData = request.data
        reqEventName = requestData['event_name']
        reqStartDate = datetime.strptime(requestData['sdate'],'%d/%m/%Y')
        reqEndDate = datetime.strptime(requestData['edate'],'%d/%m/%Y')
        fAddress = requestData['address_line1']+ "," + str(requestData['address_line2'])+ "," + requestData['state'] + "," + requestData['city'] + "," + str(requestData['pincode'])
        filterArticleData = Articles2.objects.filter(sdate=reqStartDate,edate=reqEndDate,full_address=fAddress,event_name=reqEventName)
        if len(filterArticleData) == 1:
            return Response({'dashboard': self.queryset, 'serializer':self.serializer_class,'errorMessage':'This event already exists'})
        # ends here ~ @author Shubham ~ new code to check duplicate and return an error message to UI
        #######################contact#########################
        user = Users.objects.get(pk=request.session['userid'])
        print('\n\n\n\n\n\n',user.mobile)
        if user.mobile == '' or user.mobile == 0 :
            return redirect('dashboard:updateContact')

        #######################################################

        event_md5 = md5(request.data.get('event_name').encode('utf-8')).hexdigest()[:34]
        print(event_md5)
        print("Up postttttttttttttttttt")
        context = {'md5' : event_md5}
        event_name=request.data.get('event_name')
        print(event_name)
        # l.append(event_name)
        serializer = Articles2Serializer(data=request.data, context=context)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True,'event_name':event_name})
        print(serializer)
        print("posttttttttttttttttttttttttt")
        obj = serializer.save()

        if serializer.data['webinar_link']:
            obj.full_address = ''
        else:
            venue_not_decided = request.data.get('venue_not_decided');
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
        statusPromotionObj = serializer.save()
        statusPromotionObj.step1_complete = 1
        statusPromotionObj.referrer_program_status = 1

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

        statusPromotionObj.sms_credit = int(defaultSmsCredits)
        statusPromotionObj.email_credit = int(defaultEmailCredits)
        # ends here ~ code december 24 2019

        # function for create short-url with different sources
        shortUrlSourcesList = ['organic', 'sms_marketing_organizer', 'sms_marketing_admin', 'email_marketing_organizer', 'email_marketing_admin', 'referral_marketing', 'social_organic', 'social_paid', 'organizer']
        createMultipleShortUrl(event_id,shortUrlSourcesList)
        # ends here ~ function for create short-url with different sources

        statusPromotionObj.save()
        messages.success(request, f'Thank you. Event has been registered. your event id is {event_id}')
        base_url = reverse('dashboard:step_two', kwargs={'md5':event_md5, 'event_id':event_id})
        return redirect(base_url)

class CategoryCreateAPIView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, event_id, md5, *args, **kwargs):
        #if 'userid' not in request.session.keys():
         #   return redirect('/live/login')
        request.session['event_id'] = event_id
        request.session['md5'] = md5

        # get event name from articles 2 table
        articles2Filter = Articles2.objects.get(id=event_id)
        event_name = articles2Filter.event_name
        # ends here ~ get event name from articles 2 table

        qs_categories = Categories.objects.values_list('category_id', 'category')
        return Response({'context':qs_categories, 'event_name':event_name}, template_name = 'dashboard/create-event/step_2/step_two.html')

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5']
        event_id = request.session['event_id']
        context = {'event_id' : event_id}
        print(request.data)
        serializer = CategorizedEventsSerializer(data=request.data, context=context)
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
        statusPromotionObj = serializer.save()
        statusPromotionObj.step1_complete = 1
        statusPromotionObj.step2_complete = 1
        statusPromotionObj.save()
        base_url = reverse('dashboard:step_three', kwargs={'md5':md5, 'event_id':event_id})
        return redirect(base_url)


class TopicsListAPIView(ListAPIView):
    def get(self, request):
        cat_id = request.GET.get('id')
        queryset = Topics.objects.filter(category=cat_id).order_by('topic')
        data = serializers.serialize('json', list(queryset))
        return HttpResponse(data)

class ThirdStepTemp(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, event_id, md5, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        request.session['event_id'] = event_id
        request.session['md5'] = md5
        return Response({}, template_name = 'dashboard/create-event/step_3/step_three_temp.html')

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5']
        event_id = request.session['event_id']
        base_url = reverse('dashboard:step_four', kwargs={'md5':md5, 'event_id':event_id})
        return redirect(base_url)

class DescriptionCreateAPIView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, event_id, md5, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')

        # get event name from articles 2 table
        articles2Filter = Articles2.objects.get(id=event_id)
        event_name = articles2Filter.event_name
        # ends here ~ get event name from articles 2 table

        request.session['event_id'] = event_id
        request.session['md5'] = md5
        inst = get_object_or_404(Articles2, id=event_id)

        # qs_india=get_object_or_404(AboutCountries, country=inst.country)
        # make country optional in step 3
        try:
            bankInfoFilter = AboutCountries.objects.get(country=inst.country)
            bank_regex1 = bankInfoFilter.bank_regex1
            bank_regex2 = bankInfoFilter.bank_regex2
        except Exception as e:
            bank_regex1 = '/[0-9]{9,18}/'
            bank_regex2 = '/[A-Za-z]{4}[0-9]{7}/'
        # ends here ~ make country optional in step 3

        descform = Articles2Form()
        return Response({'descform':descform, 'bank_regex1':bank_regex1,'bank_regex2':bank_regex2, 'event_name':event_name},
                        template_name = 'dashboard/create-event/step_4/step_four.html')

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5']
        event_id = request.session['event_id']
        print('== == == == == == == == == == == == == == == ==')
        print(event_id)
        print(' == Articles2 ==')
        print(Articles2)
        descform = Articles2Form(request.POST, instance = get_object_or_404(Articles2, id=event_id))

        print('descform >>',descform)
        if not descform.is_valid():
            return Response({'descform': descform,'flag':True})
        descform.save()
        StatusPromotionTicketing.objects.filter(event_id=event_id).update(step1_complete = 1, step2_complete = 1, step3_complete = 1, step4_complete = 1)
        tkt_type = StatusPromotionTicketing.objects.all().filter(event_id=event_id)
        type = tkt_type[0].ticketing
        if type == 0:
            base_url = reverse('dashboard:step_six', kwargs={'md5':md5, 'event_id':event_id})
        elif type == 1:
            base_url = reverse('dashboard:step_five', kwargs={'md5': md5, 'event_id': event_id})
        return redirect(base_url)


######################################################
# working code step 6 (old code)

# class QuestionCreateAPIView(ListCreateAPIView):
#     renderer_classes = [TemplateHTMLRenderer]

#     def get(self, request, event_id, md5, *args, **kwargs):
#         print('--------------------')
#         print(request.session.keys())
#         if 'userid' not in request.session.keys():
#             return redirect('/live/login')

#         # @author Shubham ~ send email to user on loading of step 6 ~ October 14 2019
#         #-------------------------------

#         # query for filter data from different table to get organizer email
#         filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=event_id).values('connected_user')
#         connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']

#         filterUserData = Users.objects.get(id = connectedUserId)
#         organizerEmail = filterUserData.user
#         # ends here ~ query for filter data from different table to get organizer email

#         # filter and extract required data from Articles2 Table
#         filterEventData = Articles2.objects.get(id = event_id)
#         eventName = filterEventData.event_name
#         # ends here ~ filter and extract required data from Articles2 Table

#         # send email to organizer inside try except block
#         try:
#             subject = 'Congratulations! Your '+ eventName  +' is created on Ercess Live'
#             email_from = settings.EMAIL_HOST_USER
#             recipient_list = [organizerEmail]
#             html_message = render_to_string('static/common/event_created.html', {
#                 'event_name': eventName,
#             })

#             msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
#             msg.content_subtype = "html"
#             msg.send(fail_silently=False)
#         except Exception as e:
#             print('error while send email to organizer >> ',e)
#         # ends here ~ send email to organizer inside try except block

#         StatusPromotionTicketing.objects.filter(event_id=event_id).update(step1_complete = 1, step2_complete = 1, step3_complete = 1, step4_complete = 1, step5_complete = 1)


#         #-------------------------------
#         # ends here ~ @author Shubham ~ send email to user on loading of step 6 ~ October 14 2019

#         request.session['event_id'] = event_id
#         request.session['md5'] = md5
#         inst = get_object_or_404(StatusPromotionTicketing, event_id=event_id)
#         print(inst)
#         data={'complete_details':1}
#         serializer = StatusPromotionTicketingSerializer(inst, data=data, partial=True)
#         if not serializer.is_valid():
#             return Response({'serializer': serializer,'flag':True})
#         serializer.save()
#         qs_types = AttendeeFormTypes.objects.values_list('type_id', 'name')
#         return Response({'context':qs_types}, template_name = 'dashboard/create-event/step_6/step_six.html')

#     def post(self, request, *args, **kwargs):
#         if 'userid' not in request.session.keys():
#             return redirect('/live/login')
#         md5 = request.session['md5']
#         event_id = request.session['event_id']
#         print("-------------------------------")
#         print(event_id)
#         print(request.POST.items())
#         for i,j in request.POST.items():
#             print(i,j)
#         for i,j in request.POST.items():
#             if i not in ['csrfmiddlewaretoken']:
#                 ques = request.POST.getlist(i)
#                 print(ques)
#                 type_inst = AttendeeFormTypes.objects.get(name=ques[2])
#                 type_id=type_inst.type_id
#                 add_que = AttendeeFormBuilder(event_id=event_id, ques_title=ques[1],
#                                           ques_accessibility=int(ques[0]), ques_type=type_id)
#                 add_que.save()
#                 que_id = add_que.ques_id
#                 if type_id == 5:
#                     options = ques[-1].split(',')
#                     print(options)
#                     for op in options:
#                         add_op = AttendeeFormOptions(event_id=event_id, ques_id=que_id, option_name=op)
#                         add_op.save()
#         StatusPromotionTicketing.objects.filter(event_id=event_id).update(step1_complete = 1, step2_complete = 1, step3_complete = 1, step4_complete = 1, step5_complete = 1, step6_complete = 1)
#         base_url = reverse('dashboard:event_added')
#         return HttpResponse(base_url)

# ends here ~ working code step 6 (old code)
######################################################

# @author Shubham ~ create discount coupon on creation of ticket
def createDiscountCoupon(ticketPricePar, ticketIdPar, eventIdPar, expiryDatePar, tktStartDatePar):
    try:
        # defined variables
        currTicketPrice = ticketPricePar
        currTicketId = ticketIdPar
        # ends here ~ defined variables

        # get articles 2 country name
        eventCountryName = Articles2.objects.get(id=eventIdPar)
        eventCountryName = eventCountryName.country
        # ends here ~ get discount amount

        # get country id on basis of country name
        eventCountryId = AboutCountries.objects.get(country=eventCountryName)
        eventCountryId = eventCountryId.table_id
        # ends here ~ get country id on basis of country name

        # get predefined coupon discount data
        ercessOffersFilterData = ErcessOffers.objects.filter(country=eventCountryId, price_range_min__lte=currTicketPrice, price_range_max__gte=currTicketPrice, status='active').values()
        # ends here ~ get predefined discount data

        if(len(ercessOffersFilterData) > 0):
            ercessOffersList = list(ercessOffersFilterData)
            # loop on ercessOffersList to create ticket with data
            # uniqueCouponCode = str(uuid.uuid4().hex[-2:].upper())+str(uuid.uuid4().hex[:6].upper())+str(uuid.uuid4().hex[:2].upper())
            for offers in ercessOffersList:
                TicketDiscounts.objects.create(ticket_id=currTicketId,event_id=eventIdPar,coupon=offers['coupon_name'],discount_amt=offers['discount_amt'],discount_type=1,discount_start=tktStartDatePar,discount_end=expiryDatePar,active=1)
            # ends here ~ loop on ercessOffersList to create ticket with data
    except Exception as e:
        print('condition not satisfy for create discount for ticket >> ',e)

    # ends here ~ @author Shubham ~ create discount coupon on creation of ticket

class QuestionCreateAPIView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request, event_id, md5, *args, **kwargs):
        print('--------------------')
        print(request.session.keys())
        if 'userid' not in request.session.keys():
            return redirect('/live/login')

        # get event name from articles 2 table
        articles2Filter = Articles2.objects.get(id=event_id)
        event_name = articles2Filter.event_name
        # ends here ~ get event name from articles 2 table

        # @author Shubham ~ send email to user on loading of step 6 ~ October 14 2019
        #-------------------------------

        # query for filter data from different table to get organizer email
        filterStatusPromoTkt = StatusPromotionTicketing.objects.filter(event_id=event_id).values('connected_user')
        connectedUserId = list(filterStatusPromoTkt)[0]['connected_user']

        filterUserData = Users.objects.get(id = connectedUserId)
        organizerEmail = filterUserData.user
        # ends here ~ query for filter data from different table to get organizer email

        # filter and extract required data from Articles2 Table
        filterEventData = Articles2.objects.get(id = event_id)
        eventName = filterEventData.event_name
        # ends here ~ filter and extract required data from Articles2 Table

        # send email to organizer inside try except block
        try:
            subject = 'Congratulations! Your '+ eventName  +' is created on Ercess Live'
            email_from = settings.EMAIL_HOST_USER
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
            email_from = settings.EMAIL_HOST_USER
            recipient_list = ['tickets@ercess.com']
            html_message = eventName + ' is created on Ercess Live.'
            msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
            msg.send(fail_silently=False)
        except Exception as e:
            print('error while send email to managers >> ',e)
        # ends here ~ send email to organizer inside try except block

        StatusPromotionTicketing.objects.filter(event_id=event_id).update(step1_complete = 1, step2_complete = 1, step3_complete = 1, step4_complete = 1, step5_complete = 1)


        #-------------------------------
        # ends here ~ @author Shubham ~ send email to user on loading of step 6 ~ October 14 2019

        request.session['event_id'] = event_id
        request.session['md5'] = md5
        inst = get_object_or_404(StatusPromotionTicketing, event_id=event_id)
        print(inst)
        data={'complete_details':1}
        serializer = StatusPromotionTicketingSerializer(inst, data=data, partial=True)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        serializer.save()
        qs_types = AttendeeFormTypes.objects.values_list('type_id', 'name')
        return Response({'context':qs_types, 'event_id': event_id, 'event_name':event_name}, template_name = 'dashboard/create-event/step_6/step_six.html')

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')



        md5 = request.session['md5']
        event_id = request.session['event_id']
        print("-------------------------------")
        print(event_id)
        print(request.POST.items())


        # test code
        # filterFinanceStdChrge = FinanceStandardCharges.objects.filter(service_type="paid_marketing").values()
        # paid_marketing_package_list = list(filterFinanceStdChrge)
        # # base_url = reverse('dashboard:event_added')

        # print(paid_marketing_package_list)

        # paid_marketing_packages_content = render_to_string('static/common/paid_marketing_string_tmp.html', {
        #     'packageList': paid_marketing_package_list,
        #     'event_id': event_id
        # })


        # filterFinanceStdChrge = FinanceStandardCharges.objects.filter(service_type="unlock_rsvp").values()
        # unlock_rsvp_list = list(filterFinanceStdChrge)
        # rsvp_package_content = render_to_string('static/common/rsvp_string_tmp.html', {
        #     'packageList': unlock_rsvp_list,
        #     'event_id': event_id
        # })


        # # ends here ~ test code


        for i,j in request.POST.items():
            print(i,j)
        for i,j in request.POST.items():
            if i not in ['csrfmiddlewaretoken']:
                ques = request.POST.getlist(i)
                print(ques)
                type_inst = AttendeeFormTypes.objects.get(name=ques[2])
                type_id=type_inst.type_id
                add_que = AttendeeFormBuilder(event_id=event_id, ques_title=ques[1],
                                          ques_accessibility=int(ques[0]), ques_type=type_id)
                add_que.save()
                que_id = add_que.ques_id
                if type_id == 5:
                    options = ques[-1].split(',')
                    print(options)
                    for op in options:
                        add_op = AttendeeFormOptions(event_id=event_id, ques_id=que_id, option_name=op)
                        add_op.save()
        StatusPromotionTicketing.objects.filter(event_id=event_id).update(step1_complete = 1, step2_complete = 1, step3_complete = 1, step4_complete = 1, step5_complete = 1, step6_complete = 1)

        # messageData = {'message': 'show package info.','responseType': 'success', 'messageType': 'success','paid_promo_tmp':paid_marketing_packages_content,'unlock_rsvp_tmp':rsvp_package_content}
        # messageData = {'message': 'show package info.','responseType': 'success', 'messageType': 'success','data':paid_promo_package_list}
        # return HttpResponse(json.dumps(messageData))
        base_url = reverse('dashboard:event_added', args=[event_id])
        return HttpResponse(base_url)

class CreateTicketsView(ListCreateAPIView):

    renderer_classes = [TemplateHTMLRenderer]
    # template_name = 'dashboard/duplicate_step5_tkt_list.html'
    template_name = 'dashboard/create-event/step_5/step_five.html'
    tickets = Tickets.objects.all()
    aboutcountries = AboutCountries.objects.all()
    now = datetime.now()

    #event_id = 20

    serializer_class= TicketsSerializer(context=tickets)

    def get(self, request,event_id, md5, *args, **kwargs):    # must be included
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        request.session['event_id'] = event_id
        request.session['md5'] = md5

        # get event name from articles 2 table
        articles2Filter = Articles2.objects.get(id=event_id)
        event_name = articles2Filter.event_name
        # ends here ~ get event name from articles 2 table

        inst = get_object_or_404(Articles2, id=event_id)
        print(inst.sdate)
        date = inst.sdate.strftime('%m/%d/%Y')
        sdate = inst.sdate.strftime('%d/%m/%Y')
        edate = inst.edate.strftime('%d/%m/%Y')
        eventStartTime = inst.start_time.strftime('%H:%M')
        eventEndTime = inst.end_time.strftime('%H:%M')
        
        names=[]
        prices=[]
        ticketvals= Tickets.objects.all().filter(event_id=event_id)
        print(ticketvals)
        for i in range(0,len(ticketvals)):
            names.append(ticketvals.values('ticket_name')[i]['ticket_name'])
            prices.append(ticketvals.values('ticket_price')[i]['ticket_price'])
        ticketnames = json.dumps(names)
        print(names,prices)
        ticketvalues= Tickets.objects.values()
        listdictticket = [entry for entry in ticketvalues]
        listticket=[d['event_id'] for d in listdictticket]
        flag=False
        if event_id in listticket:
            flag=True

        return Response({'ticket': ticketvalues, 'event_id': event_id , 'md5':md5,'serializer':self.serializer_class,'event_start_date':date, 'sdate':sdate, 'edate':edate,'event_start_time':eventStartTime,'event_end_time':eventEndTime,
                'a':self.aboutcountries,'cureventid':event_id,'flag':flag,'names':names,'prices':prices, 'ticketnames':ticketnames, 'event_name':event_name},
                 template_name = 'dashboard/create-event/step_5/step_five.html'  )

    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        md5 = request.session['md5']
        event_id = request.session['event_id']
        now = datetime.now()
        #context = {'event_id' : event_id}
        print(request.data)
        tsd = request.data.get('start_date')
        # exd = request.data.get('start_time_step5')

        start_t = request.POST.get('start_time_step5')

        if start_t[0] == '1' and start_t[1] != ':':
            if start_t[6:] == 'AM' and start_t[:2] != '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'AM' and start_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                start_time = now.time().replace(hour=0, minute=int(start_t[3:5]), second=0, microsecond=0)
            elif start_t[6:] == 'PM' and start_t[:2] == '12':
                start_time = now.time().replace(hour=int(start_t[:2]), minute=int(start_t[3:5]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(hour=(int(start_t[:2]) + 12), minute=int(start_t[3:5]), second=0, microsecond=0)
        else:
            if start_t[5:] == 'AM':
                start_time = now.time().replace(hour=int(start_t[0]), minute=int(start_t[2:4]), second=0, microsecond=0)
            else:
                start_time = now.time().replace(hour=(int(start_t[0]) + 12), minute=int(start_t[2:4]), second=0, microsecond=0)

        exd=str(start_time)


        sd = request.data.get('end_date')
        # xd = request.data.get('end_time_step5')

        end_t = request.POST.get('end_time_step5')


        if end_t[0] == '1' and end_t[1] != ':':
            if end_t[6:] == 'AM' and end_t[:2] != '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'AM' and end_t[:2] == '12':
                # print("herrrrrrrrrrrrreeeeeeeeeeeeeeeeeeeeeeeeeee")
                end_time = now.time().replace(hour=0, minute=int(end_t[3:5]), second=0, microsecond=0)
            elif end_t[6:] == 'PM' and end_t[:2] == '12':
                end_time = now.time().replace(hour=int(end_t[:2]), minute=int(end_t[3:5]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(hour=(int(end_t[:2]) + 12), minute=int(end_t[3:5]), second=0, microsecond=0)
        else:
            if end_t[5:] == 'AM':
                end_time = now.time().replace(hour=int(end_t[0]), minute=int(end_t[2:4]), second=0, microsecond=0)
            else:
                end_time = now.time().replace(hour=(int(end_t[0]) + 12), minute=int(end_t[2:4]), second=0, microsecond=0)


        xd=str(end_time)


        print(exd,xd)
        total_qty = request.data.get('ticket_qty')
        print(tsd + exd )
        print(exd)
        ticket_start_date = tsd +" "+ exd
        ticket_start_date = datetime.strptime(ticket_start_date, '%d/%m/%Y %H:%M:%S')
        expiry_date= sd +" "+ xd
        expiry_date= datetime.strptime(expiry_date, '%d/%m/%Y %H:%M:%S')
        context = {'ticket_start_date' : ticket_start_date,'expiry_date' :  expiry_date, 'event_id' : event_id, 'qty_left' : total_qty, 'ercess_fee': 1, 'transaction_fee':1}
        serializer = TicketsSerializer(data=request.data,  context = context)
        print("hi is this code running")
        print(serializer)
        if not serializer.is_valid():
            return Response({'serializer': serializer,'flag':True})
        # serializer.save()

        # @author Shubham ~ 20 nov 2019 ~ modify old code
        ticketSave = serializer.save()
        print("data stored in table")
        print('md5 is {} and event_id is {}'.format(md5, event_id))

        # call function to create discount coupon on creation of ticket
        createDiscountCoupon(ticketSave.ticket_price, ticketSave.tickets_id, event_id, expiry_date, ticket_start_date)
        # ends here ~ call function to create discount coupon on creation of ticket

        base_url = reverse('dashboard:step_five', kwargs={'md5':md5, 'event_id':event_id})
        return redirect(base_url)
        # ends here ~ @author Shubham ~ 20 nov 2019 ~ modify old code

class BankDetailsView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    serializer_class= BankDetailsSerializer
    template_name = 'dashboard/bankdetails.html'
    bankdetailscontents = BankDetails.objects.all()


    def get(self, request, *args, **kwargs):
        bankdetailscontents = BankDetails.objects.all()
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        user_id = request.session.get('userid')
        for uid in bankdetailscontents:
            if (uid.user_id==user_id):
                return Response({'serializer':self.serializer_class,'i':uid, 'flag':False}, template_name = 'dashboard/bankdetails.html')
        return Response({'serializer':self.serializer_class,'flag':True}, template_name = 'dashboard/bankdetails.html')


    def post(self, request, *args, **kwargs):
        context = {'user_id': request.session.get('userid')}
        serializer = BankDetailsSerializer(data=request.data, context=context)

        requestData = request.data
        bankName = requestData['bank_name']
        accHolderName = requestData['ac_holder_name']
        accNumber = requestData['ac_number']
        ifscCode = requestData['ifsc_code']
        gstNumber = requestData['gst_number']
        user_id = request.session.get('userid')
        user=Users.objects.get(id=user_id)



        if not serializer.is_valid():
            print(serializer.errors)
            return Response({'serializer': serializer,'flag':True})
        serializer.save()

        # @author Shubham ~ send email to user on adding bank account
        subject = 'Your bank details are added successfully'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user.user]

        html_message = render_to_string('static/common/bank_details_template.html', {
            'bankName': bankName,
            'accHolderName': accHolderName,
            'accNumber': accNumber,
            'ifscCode': ifscCode,
            'gstNumber': gstNumber,
        })

        msg = EmailMessage(subject, html_message, email_from, recipient_list, headers={'Reply-To': 'tickets@ercess.com'})
        msg.content_subtype = "html"
        msg.send(fail_silently=False)

        return redirect('/live/dashboard/bank-details')


# for edit bank details
class EditBankDetailsView(ListCreateAPIView):
    renderer_classes = [TemplateHTMLRenderer]
    serializer_class= BankDetailsSerializer
    template_name = 'dashboard/bankdetails.html'
    bankdetailscontents = BankDetails.objects.all()


    def get(self, request, *args, **kwargs):
        bankdetailscontents = BankDetails.objects.all()
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        user_id = request.session.get('userid')
        for uid in bankdetailscontents:
            if (uid.user_id==user_id):
                return Response({'serializer':self.serializer_class,'i':uid, 'flag':False}, template_name = 'dashboard/bankdetails.html')
        return Response({'serializer':self.serializer_class,'flag':True}, template_name = 'dashboard/bankdetails.html')


    def post(self, request, *args, **kwargs):
        if 'userid' not in request.session.keys():
            return redirect('/live/login')
        currentUserId = request.session.get('userid')
        bankDetailsData = request.data

        bankName = bankDetailsData['bank_name']
        acHolderName = bankDetailsData['ac_holder_name']
        acType = bankDetailsData['ac_type']
        acNumber = bankDetailsData['ac_number']
        ifscCode = bankDetailsData['ifsc_code']
        branch = bankDetailsData['branch']
        gstNumber = bankDetailsData['gst_number']

        # print(' > currentUserId > ',currentUserId)

        BankDetails.objects.filter(user_id=currentUserId).update(bank_name=bankName, ac_holder_name=acHolderName, ac_type=acType, ac_number=acNumber, ifsc_code=ifscCode, branch=branch, gst_number=gstNumber)

        return redirect('/live/dashboard/bank-details')
def createMultipleShortUrl(event_id, sourcesPar):
    try:
        sourcesList = sourcesPar

        for source in sourcesList:
            shortUrl = url_shortner.create(event_id,'',source)
    except Exception as e:
        print('error in createMultipleShortUrl function >> ',e)



############################################ TicketSaga API View ########################################################

class Index(APIView):
    def get(self,request,format=None):
        try:
            categories = CategorizedEvent.objects.all()
            category_serializers = CategorizedEventsSerializer(categories,many=True)
            return Response(category_serializers.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message":e},status=status.HTTP_400_BAD_REQUEST)

class TicketDetails(APIView):

    def get(self,request,format=None):
        try:
            current_event = Articles2.objects.get(event_id=request.session['current_event'])
            response_data = {}
            response_data['event_name'] = request.session['event_name']
            response_data['event_start'] = current_event.event_start
            response_data['event_end'] = current_event.event_end
            response_data['event_image'] = current_event.image
            response_data['numberOfTickets'] = request.session['numberOfTickets']
            event_organizer = Users.objects.get(id=current_event.organizer_id)
            response_data['organizer_name'] = organizer_obj.first_name
            response_data['organizer_contact_number'] = organizer_obj.phone
            response_data['organizer_email_id'] = organizer_obj.email
            response_data['booking_id'] = request.session['booking_id']
            response_data['final_amount'] =request.session['final_price_sum']
            print(request.session['final_price_sum'])
            response_data['first_name'] = request.session['first_name']
            response_data['email'] = request.session['email']
            response_data['phone_number'] = request.session['phone_number']
            if current_event.event_type=='physical':
                response_data['location'] = current_event.city+' '+current_event.state+' '+current_event.country+' '
            else:
                response_data['location'] = 'Online'

            subject = 'Your ticket purchase confirmation - '+response_data['event_name']
            email_from = settings.EMAIL_HOST_USER
            html_message = render_to_string('purchase_confirmation.html', {
                'event_name': response_data['event_name'],
                'amount_paid': response_data['final_amount'],
                'sold': response_data['numberOfTickets'],
                'name': response_data['first_name'],
                'contactnumber': response_data['phone_number'],
                'email':response_data['email'],
                'organizer_email': response_data['organizer_email_id'],
                'tickets':response_data['numberOfTickets'],
                'booking_id': response_data['booking_id'],
                'organizer_name': response_data['organizer_name'],
                'organizer_location':response_data['location'],
                'organization_contact_number':response_data['organizer_contact_number'],
                'send_to':response_data['email']
            })
            org_list = [response_data['organizer_email_id'],response_data['email']]
            org_msg = EmailMessage(subject, html_message, email_from, org_list, headers={'Reply-To': 'no-reply@ercess.com'})
            org_msg.content_subtype = "html"
            org_msg.send(fail_silently=False)
            return Response({"message":"Mail sent successfully"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message":e},status=status.HTTP_400_BAD_REQUEST)

class EventsIn(APIView):
    def get(self,request,cityname,state,format=None):
        try:
            city = cityname
            state = state
            print(state)
            city_list = city.split(',')
            if len(city_list) == 2:
                city_name = city_list[0].strip()
                state_name = city_list[0].strip()
            elif len(city_list) >= 3:
                city_name = city_list[0].strip()
                state_name = city_list[1].strip()
            elif len(city_list) == 1:
                city_name = city_list[0].strip()
                state_name = city_list[0].strip()
            categories = CategorizedEvent.objects.all()
            category_serializers = CategorizedEventsSerializer(categories,many=True)
            current_events = Articles2.objects.filter(city =city_name, state = state_name,event_end__gt=timezone.now()).order_by('event_start')
            webinar_events = Articles2.objects.filter(event_end__gt=timezone.now(),webinar_link__isnull=True).order_by('event_start')
            current_events = current_events | webinar_events
            current_events_serializer = EventSerializers(current_events,many=True)

            context = {
                'cityname' : city_name,
                'statename':state,
                'query_city': cityname,
                'Categories':category_serializers.data,
                'events_list':current_events_serializer.data,
            }
            return Response(context,status=status.HTTP_200_OK)
        except:
            return Response({"message":e},status=status.HTTP_400_BAD_REQUEST)

class CategoryEventsList(APIView):
    def get(self,request,categoryname,format=None):
        try:
            category_obj = Category.objects.get(category=categoryname)
            event_category_list = CategorizedEvents.objects.filter(category_id=category_obj.category_id)
            categories = CategorizedEvent.objects.all()
            category_serializers = CategorizedEventsSerializer(categories,many=True)
            events_id_list = []
            for event_category in event_category_list:
                event_id = event_category.ec_event_id
                events_id_list.append(event_id)
                event = Articles2.objects.get(event_id=event_id)
                events_list.append(event)

            events = Articles2.objects.exclude(eDate<=timezone.now()).filter(event_id__in=events_list)
            current_events_serializer = EventSerializers(events,many=True)
            context = {
                'cityname' : city_name,
                'statename':state,
                'query_city': cityname,
                'Categories':category_serializers.data,
                'events_list':current_events_serializer.data,
            }
            return Response(context,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message":e},status=status.HTTP_400_BAD_REQUEST)

