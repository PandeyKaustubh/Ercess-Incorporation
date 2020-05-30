from django.shortcuts import render
from rest_framework.response import Response
from datetime import datetime
import json
from django.urls import reverse
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from django.contrib import messages
from django.conf import settings
from django.core.mail import  send_mail
import hashlib,pycountry
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from rest_framework.views import APIView
from dashboard.models import (Articles2, Categories, CategorizedEvents,Topics, StatusPromotionTicketing,
                              AttendeeFormTypes, AttendeeFormOptions, AttendeeFormBuilder,
                              Tickets, AboutCountries, BankDetails, FinanceStandardCharges, TicketDiscounts,
                              ErcessOffers, Stall, StallsProducts, StallsAudience, CategoriesStalls, StallAudience,
                              StallFacilities, StallUpload)
from .serializers import *

from rest_framework import status
# Create your views here.

class TicketDetails(APIView):

    def get(self,request,format=None):
        try:
            current_event = Articles2.objects.get(event_id=request.data['current_event'])
            response_data = {}
            response_data['event_name'] = request.data['event_name']
            response_data['event_start'] = current_event.event_start
            response_data['event_end'] = current_event.event_end
            response_data['event_image'] = current_event.image
            response_data['numberOfTickets'] = request.data['numberOfTickets']
            event_organizer = Users.objects.get(id=current_event.organizer_id)
            response_data['organizer_name'] = organizer_obj.first_name
            response_data['organizer_contact_number'] = organizer_obj.phone
            response_data['organizer_email_id'] = organizer_obj.email
            response_data['booking_id'] = request.data['booking_id']
            response_data['final_amount'] =request.data['final_price_sum']
            print(request.data['final_price_sum'])
            response_data['first_name'] = request.data['first_name']
            response_data['email'] = request.data['email']
            response_data['phone_number'] = request.data['phone_number']
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

class CategoryList(APIView):
    def get(self,request,format=None):
        categories = Categories.objects.all()
        category_serializers = CategoriesSerialzier(categories,many=True)
        return Response(category_serializers.data,status=status.HTTP_200_OK)

class CityEventListing(APIView):
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
            current_events = Articles2.objects.filter(city =city_name, state = state_name)
            webinar_events = Articles2.objects.filter(edate__gt=timezone.now(),webinar_link__isnull=True)
            current_events = current_events | webinar_events

            current_events_serializer = Articles2Serializer(current_events,many=True)
            response_data = {
                'cityname' : city_name,
                'statename':state,
                'query_city': cityname,
                'events_list':current_events_serializer.data,
            }
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

class CategoryEventsListing(APIView):
    def get(self,request,categoryname,format=None):
        try:
            category_obj = Categories.objects.get(category=categoryname)
            event_category_list = CategorizedEvents.objects.filter(category_id=category_obj.category_id)
            events_id_list = []
            for event_category in event_category_list:
                event_id = event_category.event_id
                try:
                    event = Articles2.objects.get(id=event_id)
                    events_id_list.append(event_id)
                    events_list.append(event)
                except:
                    continue

            events = Articles2.objects.exclude(edate__lt=timezone.now()).filter(id__in=events_id_list)
            current_events_serializer = Articles2Serializer(events,many=True)
            response_data = {
                'categoryname': categoryname,
                'events_list':current_events_serializer.data,
            }
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            error_response = {
                'message': '404 Not Found',
            }
            return Response(error_response,status=status.HTTP_400_BAD_REQUEST)

class SubCategoryEventListing(APIView):
    def get(self,request,categoryname,subcategoryname,format=None):
        try:
            subcategory_obj = Topics.objects.get(topic=subcategoryname)
            event_category_list = CategorizedEvents.objects.filter(topic_id=subcategory_obj.topics_id)
            events_id_list = []
            for event_category in event_category_list:
                event_id = event_category.event_id
                try:
                    event = Articles2.objects.get(id=event_id)
                    events_id_list.append(event_id)
                    events_list.append(event)
                except:
                    continue

            events = Articles2.objects.exclude(edate__lt=timezone.now()).filter(id__in=events_id_list)
            current_events_serializer = Articles2Serializer(events,many=True)
            response_data = {
                'categoryname' : categoryname,
                'subcategoryname': subcategoryname,
                'events_list':current_events_serializer.data,
            }
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            error_response = {
                'message': '404 Not Found',
            }
            print(e)
            return Response(error_response,status=status.HTTP_400_BAD_REQUEST)

class OnlineSubCategoryEventListing(APIView):
    def get(self,request,categoryname,subcategoryname,format=None):
        try:
            subcategory_obj = Topics.objects.get(topic=subcategoryname)
            event_category_list = CategorizedEvents.objects.filter(topic_id=subcategory_obj.topics_id)
            events_id_list = []
            for event_category in event_category_list:
                event_id = event_category.event_id
                try:
                    event = Articles2.objects.get(id=event_id)
                    events_id_list.append(event_id)
                    events_list.append(event)
                except:
                    continue

            events = Articles2.objects.exclude(edate__lt=timezone.now()).filter(id__in=events_id_list,webinar_link__isnull=False)
            current_events_serializer = Articles2Serializer(events,many=True)
            response_data = {
                'categoryname' : categoryname,
                'subcategoryname': subcategoryname,
                'events_list':current_events_serializer.data,
            }
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            error_response = {
                'message': '404 Not Found',
            }
            print(e)
            return Response(error_response,status=status.HTTP_400_BAD_REQUEST)


class EventDetailView(APIView):
    def get(self,request,event_name,event_id):
        try:
            current_event = Articles2.objects.get(id=event_id)
            current_events_serializer = Articles2Serializer(current_event)
            expired = False
            if(current_event.edate<=timezone.now()):
                expired = True

            coupon_name = ''
            event_discount_data = None
            try:
                discount_obj = TicketDiscounts.objects.get(event_id=event_id)
                discount_obj_serializer = TicketsSerializer(discount_obj)
                event_discount_data = discount_obj_serializer.data
                coupon_name = discount_obj.coupon
            except:
                coupon_name = ''
            active = False
            if current_event.sdate<=timezone.now() and current_event.sdate>=timezone.now():
                active=True
            messages = []
            try:
                current_ticket_object = Tickets.objects.filter(event_id=current_event.id)
            except:
                current_ticket_object = None

            latitude = current_event.latitude
            longitude = current_event.longitude

            response_data = {
                'current_event' :current_events_serializer.data,
                'messages':messages,
                'event_id':event_id,
                'tickets':event_discount_data,
                'expired':expired,
                'coupon':coupon_name,
                'active':active,
            }
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            response_message = {
                'message' : '404 N0T FOUND'
            }
            return Response(response_message,status=status.HTTP_404_NOT_FOUND)


class OnlineEventListing(APIView):
    def get(self,request,format=None):
        try:
            webinar_events = Articles2.objects.filter(edate__gt=timezone.now(),webinar_link__isnull=False)
            current_events_serializer = Articles2Serializer(webinar_events,many=True)
            response_data = {
                'Events' : 'online events',
                'events_list':current_events_serializer.data,
            }
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

class OnlineCategoryEventListing(APIView):
    def get(self,request,categoryname,format=None):
        try:
            category_obj = Categories.objects.get(category=categoryname)
            event_category_list = CategorizedEvents.objects.filter(category_id=category_obj.category_id)
            events_id_list = []
            for event_category in event_category_list:
                event_id = event_category.event_id
                try:
                    event = Articles2.objects.get(id=event_id)
                    events_id_list.append(event_id)
                except Exception as e:
                    print(e)
                    continue
            events = Articles2.objects.filter(edate__gt=timezone.now(),id__in=events_id_list,webinar_link__isnull=False)
            current_events_serializer = Articles2Serializer(events,many=True)
            response_data = {
                'event_type' : 'online',
                'categoryname': categoryname,
                'events_list':current_events_serializer.data,
            }
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            error_response = {
                'message': '404 Not Found',
            }
            return Response(error_response,status=status.HTTP_400_BAD_REQUEST)


class Booking(APIView):

    def getCurrency(self,current_event):
        try:
            country = pycountry.countries.get(name=current_event.country.capitalize())
            currency = pycountry.currencies.get(numeric=country.numeric)
            return currency.alpha_3
        except Exception as e:
            return "INR"

    def post(self,request,event_id,source):
        current_event = Articles2.objects.get(id=event_id)
        response_data = {}
        response_data['currency'] = self.getCurrency(current_event)
        event_tickecting_type = StatusPromotionTicketing.objects.get(event_id=event_id).ticketing
        if event_tickecting_type==1:
            try:
                try:
                    quantity = [int(q) for q in request.data['quantity']]
                    total_price = float(request.data['total_price'])
                except:
                    quantity = 0
                    total_price = 0
                
                ticket_ids = request.data['ticket_ids']
                total_flat_charge = 0
                total_percent_charge = 0
                total_extra_charge = 0
                removed_ticket_ids = []
                final_amount = 0
                percent_sum  = 0
                q = 0
                for index in range(len(ticket_ids)):
                    ticket = ticket_ids[index]
                    temp_quantity = quantity[index]
                    if temp_quantity == 0:
                        continue
                    removed_ticket_ids.append(ticket)
                    ticket_objs = Tickets.objects.get(tickets_id=ticket)
                    final_amount = int(ticket_objs.ticket_price)*int(temp_quantity)
                    if ticket_objs.other_charges == None:
                        total_extra_charge = 0
                    if int(ticket_objs.other_charges_type) == 1:
                        if ticket_objs.other_charges:
                            total_flat_charge = total_flat_charge + (int(temp_quantity) * int(ticket_objs.other_charges))
                    elif int(ticket_objs.other_charges_type)==0:
                        if ticket_objs.other_charges:
                            percent = int(ticket_objs.other_charges) / 100
                            percent_sum = percent_sum + int(ticket_objs.other_charges)
                            temp_ticket_price = ticket_objs.ticket_price * percent
                            total_percent_charge = total_percent_charge + (temp_ticket_price * temp_quantity)
                            print(total_percent_charge)
                    final_amount = final_amount+total_percent_charge+total_flat_charge
                response_data['event_name'] = current_event.event_name
                response_data['event_start'] = current_event.sdate.strftime("%d/%m/%y")
                response_data['event_end'] = current_event.edate.strftime("%d/%m/%y")
                response_data['ticket_price'] = total_price
                response_data['extra_flat_charges'] = total_flat_charge
                response_data['extra_percent_charges'] = total_percent_charge
                response_data['percent_sum'] = percent_sum
                response_data['ticket_ids']  = removed_ticket_ids
                response_data['numberOfTickets'] = sum(quantity)
                response_data['final_amount'] = final_amount
                response_data['current_event'] = event_id
                return Response(response_data,status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                response_data['event_name'] = current_event.event_name
                response_data['event_start'] = current_event.sdate.strftime("%d/%m/%y")
                response_data['event_end'] = current_event.edate.strftime("%d/%m/%y")
                response_data['event_ticket_type'] = 'Free'
                response_data['ticket_price'] = 0
                response_data['final_price_sum'] = 0

                try:
                    print(request.data['quantity'])
                    quantity = [int(q) for q in request.data['quantity']]
                    total_price = float(request.data['total_price'])
                except:
                    quantity = 0
                    total_price = 0
                ticket_ids = request.POST.getlist('ticket_ids')
                response_data['ticket_ids'] = ticket_ids
                response_data['numberOfTickets'] = sum(quantity)
                response_data['current_event'] = event_id
                response_data['source'] = source
                return Response(response_data,status=status.HTTP_200_OK)
            except Exception as e:
                print(e)
                return Response(status=status.HTTP_400_BAD_REQUEST)
    def get(self,request,event_id,source):
        response_data = {}
        current_event = Articles2.objects.get(id=event_id)
        response_data['currency'] = self.getCurrency(current_event)
        current_events_serializer = Articles2Serializer(current_event)
        response_data['event'] = current_events_serializer.data
        response_data['current_date'] = timezone.now()
        response_data['source'] = source
        coupon_name = ''
        event_tickecting_type = StatusPromotionTicketing.objects.get(event_id=event_id).ticketing
        response_data['event_ticket_type'] = event_tickecting_type
        event_discount_data = None
        try:
            discount_obj = TicketDiscounts.objects.get(event_id=event_id)
            discount_obj_serializer = TicketsSerializer(discount_obj)
            event_discount_data = discount_obj_serializer.data
            coupon_name = discount_obj.coupon
        except:
            coupon_name = ''

        avail_tickets = Tickets.objects.filter(event_id=event_id, expiry_date__gte=timezone.now())
        if avail_tickets.exists():
            response_data['show_proceed_btn'] = True
        else:
            response_data['show_proceed_btn'] = False
        try:
            ticket_objs = Tickets.objects.filter(event_id=event_id,expiry_date__gte=timezone.now())
            if ticket_objs:
                print(ticket_objs)
                tickets_objs_serializer = TicketsSerializer(ticket_objs,many=True)
                total_tickets_price = 0
                response_data['total_tickets_price'] = total_tickets_price
                response_data['tickets'] = tickets_objs_serializer.data
                response_data['coupon'] = coupon_name 
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)

class FreeCheckout(APIView):
    def get(self,request,source):
        try:
            response_data = {}
            response_data['event_name'] = request.data['event_name']
            response_data['source'] = source
            response_data['event_start'] = request.data['event_start']
            response_data['event_end'] = request.data['event_end']
            response_data['ticket_ids'] = request.data['ticket_ids']
            response_data['numberOfTickets'] = request.data['numberOfTickets']
            return Response(response_data,status=status.HTTP_200_OK)
        except:
            return Response(response_data,status=status.HTTP_400_BAD_REQUEST)

    def post(self,request,source):
        try:
            response_data = {}
            response_data['first_name'] = request.data['firstname']
            response_data['last_name'] = request.data['lastname']
            response_data['email'] = request.data['email']
            response_data['phone_number'] = request.data['phone_number']
            response_data['ticket_price'] = 0
            response_data['final_price_sum'] = 0
            response_data['event_ticket_type'] = 'Free'
            response_data['source'] =source
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class Checkout(APIView):

    def get(self,request):
        response_data =  {}
        response_data['event_name'] = request.data['event_name']
        response_data['source'] = request.data['source']
        response_data['event_start'] = request.data['event_start']
        response_data['event_end'] = request.data['event_end']
        response_data['ticket_price'] = request.data['ticket_price']
        response_data['extra_flat_charges'] = request.data['extra_flat_charges']
        response_data['extra_percent_charges'] = request.data['extra_percent_charges']
        response_data['extra_charge'] = request.data['extra_flat_charges']+request.data['extra_percent_charges']
        response_data['ticket_ids'] = request.data['ticket_ids']
        response_data['numberOfTickets'] = request.data['numberOfTickets']
        response_data['percent_sum'] = request.data['percent_sum']
        response_data['final_price_sum'] = response_data['ticket_price'] + response_data['extra_flat_charges'] + response_data['extra_percent_charges']
        request.data['final_price_sum'] = response_data['final_price_sum']
        request.data['couponactive'] = False
        return Response(response_data,status=status.HTTP_200_OK)


class PaymentDetails(APIView):
    def get(self,request):
        try:
            data = {}
            current_event = request.data['current_event']
            final_price = request.data['final_price_sum']
            numberOfTickets = request.data['numberOfTickets']
            source = request.data['source']
            txnid = get_transaction_id()
            booking_id = generate_booking_id()
            hash_ = generate_hash(request, txnid,current_event,source)
            hash_string = get_hash_string(request, txnid,current_event,source)
            coupon_id = None
            amount_deducted = None
            if 'amount_deducted' in request.data:
                amount_deducted = request.data['amount_deducted']
            try:
                if 'coupon' in request.session:
                    coupon_id = TicketDiscounts.objects.filter(coupon=request.data['coupon'])[0].table_id
            except Exception as e:
                coupon_id = None


            data["action"] = settings.PAYMENT_URL_TEST
            data["amount"] = float(final_price)
            data["productinfo"] = settings.PAID_FEE_PRODUCT_INFO
            data["key"] = settings.TEST_KEY
            data["txnid"] = txnid
            data["hash"] = hash_
            data["hash_string"] = hash_string
            data["service_provider"] = settings.SERVICE_PROVIDER
            #data["furl"] = request.build_absolute_uri(reverse("payment_failure"))
            #data["surl"] = request.build_absolute_uri(reverse("payment_success"))
            data["current_event"] = current_event
            data["current_ticket_object"] = request.data['current_event']
            data['numberOfTickets'] = numberOfTickets
            data['firstname'] = request.data['first_name']
            data['last_name'] = request.data['last_name']
            data['final_price'] = final_price
            data['coupon'] = coupon_id
            data['email'] = request.data['email']
            data['source'] = source
            data['phone'] = request.data['phone_number']
            return Response(data,status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class FreeEventAttendeeForm(APIView):
    def get(self,request):
        try:
            current_event = request.data['current_event']
            response_data = {}
            response_data['quantity'] = range(request.data['numberOfTickets'])
            source = request.data['source']
            form_build_list = []
            form_builder = AttendeeFormBuilder.objects.filter(event_id=current_event)
            check_question_list = []
            for build in form_builder:
                temp_dict = {}
                if build.ques_title in check_question_list:
                    continue
                else:
                    temp_dict['title'] = build.ques_title
                    temp_dict['question_id'] = build.id
                    check_question_list.append(build.ques_title)
                type_obj = AttendeeFormTypes.objects.filter(type_id=build.ques_type)
                temp_dict['type'] = type_obj.name
                form_build_list.append(temp_dict)
            response_data['form_options'] = AttendeeFormOptions.objects.filter(event_id=current_event)
            response_data['form_build_list'] = form_build_list
            response_data['source'] = source
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            message_data = {'message' : 'HTTP_400_BAD_REQUEST'}
            return Response(message_data,status=status.HTTP_400_BAD_REQUEST)


class EventAttendeeForm(APIView):
    def get(self,request):
        try:
            current_event = request.data['udf2']
            response_data = {}
            response_data['quantity'] = range(request.data['udf1'])
            source = request.data['udf3']
            form_build_list = []
            form_builder = AttendeeFormBuilder.objects.filter(event_id=current_event)
            check_question_list = []
            for build in form_builder:
                temp_dict = {}
                if build.ques_title in check_question_list:
                    continue
                else:
                    temp_dict['title'] = build.ques_title
                    temp_dict['question_id'] = build.id
                    check_question_list.append(build.ques_title)
                type_obj = AttendeeFormTypes.objects.filter(type_id=build.ques_type)
                temp_dict['type'] = type_obj.name
                form_build_list.append(temp_dict)
            response_data['form_options'] = AttendeeFormOptions.objects.filter(event_id=current_event)
            response_data['form_build_list'] = form_build_list
            response_data['source'] = source
            return Response(response_data,status=status.HTTP_200_OK)
        except Exception as e:
            message_data = {'message' : 'HTTP_400_BAD_REQUEST'}
            return Response(message_data,status=status.HTTP_400_BAD_REQUEST)

def generate_booking_id():
    res = ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k = 8))
    return res


def generate_hash(request, txnid,event_id,source):
    try:
        print(request.data)
        # get keys and SALT from dashboard once account is created.
        # hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
        hash_string = get_hash_string(request,txnid,event_id,source)
        generated_hash = hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()
        return generated_hash
    except Exception as e:
        # log the error here.
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None

def get_placeId():
    query_string = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng=&key=")


def get_hash_string(request, txnid,event_id,source):
    numberOfTickets = str(request.data['numberOfTickets'])
    price = request.data['final_price_sum']
    hash_string = settings.TEST_KEY+"|"+txnid+"|"+str(float(price))+"|"+settings.PAID_FEE_PRODUCT_INFO+"|"
    hash_string += request.data['first_name'] +"|"+request.data['email']+"|"+numberOfTickets + "|"+str(event_id)+"|"+str(source)
    hash_string += "||||||||"+settings.TEST_SALT
    return hash_string

def get_transaction_id():
    hash_object = hashlib.sha256(str(randint(0,9999)).encode("utf-8"))
    # take approprite length
    txnid = hash_object.hexdigest().lower()[0:32]
    return txnid

