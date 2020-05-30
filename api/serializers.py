import hashlib
import datetime
from rest_framework import serializers

import re
from dashboard.models import Articles2,Categories, CategorizedEvents, StatusPromotionTicketing, Topics,Tickets, BankDetails, Stall, StallFacilities, StallUpload
from django.utils import timezone

class Articles2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Articles2
        fields = ['event_name','website', 'sdate', 'start_time', 'edate', 'end_time', 'webinar_link', 
         'address_line1', 'address_line2', 'city', 'state', 
        'country', 'pincode','latitude','longitude','place_id','date_added']
        # read_only_fields = ['date_added']
       # extra_kwargs = {'md5': {'write_only': True}}

    date_added = serializers.HiddenField(default=timezone.now)
    event_name = serializers.CharField(
                max_length=200,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_1/eventname.html',
                },
            )

    website = serializers.CharField(
                      max_length=200,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/website.html',
                      },
                    )
    sdate =serializers.DateTimeField(
                        input_formats=['%d %b %Y %H:%M:%S %Z'],
                        style={
                          'template': 'dashboard/create-event/step_1/startdate.html'}                      
                        )

    start_time =serializers.TimeField(
                        input_formats=['%I:%M %p'],
                        style={
                          'template': 'dashboard/create-event/step_1/stime.html'}
                        )
    edate =serializers.DateTimeField(
                        input_formats=['%d %b %Y %H:%M:%S %Z'],
                        style={
                          'template': 'dashboard/create-event/step_1/enddate.html'}
                        )

   
    
    end_time =serializers.TimeField(
                        input_formats=['%I:%M %p'],
                        style={
                          'template': 'dashboard/create-event/step_1/etime.html'}
                        )
    
    webinar_link = serializers.CharField(
                        max_length=200,
                        required=False,
                        style={
                           'template': 'dashboard/create-event/step_1/webinar_radio.html'
                        }
                    )

    address_line1 = serializers.CharField(
                      max_length=200,
                      required=False,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/address1.html',
                      },
                    )
    
    address_line2 = serializers.CharField(
                      max_length=200,
                      required=False,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/address2.html',
                      },
                    )
    
    city = serializers.CharField(
                      max_length=200,
                      required=False,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/city.html',
                      },
                    )

    state = serializers.CharField(
                      max_length=200,
                      required=False,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/state.html',
                      },
                    )

    country = serializers.CharField(
                      max_length=200,
                      required=False,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/country.html',
                      },
                    )

    pincode = serializers.CharField(
                      max_length=200,
                      required=False,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/pin.html',
                      },
                    )

    latitude = serializers.CharField(

                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/latitude.html',
                      },
                      required=False,
                    )

    longitude = serializers.CharField(

                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/longitude.html',
                      },
                      required=False,
                    )

    place_id = serializers.CharField(
                      max_length=200,
                      style={
                        'autofocus': True,
                        'template': 'dashboard/create-event/step_1/place_id.html',
                      },
                      required=False,
                    )



    def validate(self, validated_data, *args, **kwargs):
        sDate = validated_data.get('sdate')
        eDate = validated_data.get('edate')
        Stime = validated_data.get('start_time')
        Etime = validated_data.get('end_time')
        web = validated_data.get('website')
        if len(web) < 10:
            raise serializers.ValidationError({"Website":"Please complete the website link."})
        if sDate > eDate:
            raise serializers.ValidationError({"End Date":"Start Date cannot be greater than End Date"})
        elif sDate == eDate and Stime == Etime:
            raise serializers.ValidationError({"End time":"Start time cannot be greater than End time"})
        validated_data['md5'] = self.context['md5']
        return validated_data

class CategorizedEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorizedEvents
        fields = ['topic_id', 'category_id' ]

    def validate(self, validated_data, *args, **kwargs):
        if validated_data['topic_id']  == 0:
            validated_data['topic_id'] = None
        validated_data['event_id'] = self.context['event_id']
        return validated_data


class TicketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tickets
        fields = ['tickets_id','ticket_name','ticket_price','other_charges','other_charges_type',
                  'ticket_qty','min_qty','max_qty','ticket_start_date','expiry_date',
                  'ticket_msg','ticket_label',
         ]
    tickets_id = serializers.IntegerField()
    ticket_name = serializers.CharField(
                max_length=200,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/ticketname.html',
                },
            )
    ticket_price = serializers.CharField(
                max_length=8,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/ticketprice.html',
                },
            )
    other_charges = serializers.CharField(required = False,
                max_length=6,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/extracharges.html',
                },
            )
    #othercharges type will come here        
    other_charges_type = serializers.IntegerField(required = False,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/extrachargestype.html',
                },
            )            
    ticket_qty = serializers.IntegerField(
                
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/ticketqty.html',
                },
            )
    min_qty = serializers.IntegerField(
                
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/ticketmin.html',
                },
            )                 
    max_qty = serializers.IntegerField(
                
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/ticketmax.html',
                },
            )                                
    ticket_start_date = serializers.DateTimeField(
                        input_formats=['%d %b %Y %H:%M:%S %Z'],
                         style={
                           'template': 'dashboard/create-event/step_5/startdate.html'}                      
                         )
    '''
    start_time_step5 = serializers.TimeField(
                         input_formats=['%I:%M %p'],
                         style={
                           'template': 'dashboard/create-event/step_5/stime.html'}
                         )
    '''
    expiry_date =serializers.DateTimeField(
                        input_formats=['%d %b %Y %H:%M:%S %Z'],
                         style={
                           'template': 'dashboard/create-event/step_5/enddate.html'}
                         )

   
    '''
    end_time_step5 =serializers.TimeField(
                         input_formats=['%I:%M %p'],
                         style={
                           'template': 'dashboard/create-event/step_5/etime.html'}
                         )
    '''
    ticket_msg = serializers.CharField(required=False,
                max_length=200,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/anymessage.html',
                },
            )
    #ticket label will come here
    ticket_label = serializers.CharField(
                max_length=200,
                style={
                    'autofocus': True,
                    'template': 'dashboard/create-event/step_5/ticketlabel.html',
                },
            )


    def validate(self, validated_data, *args, **kwargs):
        print("this is date validation")
        sDate = validated_data.get('ticket_start_date')
        eDate = validated_data.get('expiry_date')
        print(sDate)
        print(eDate)
        if sDate > eDate:
            raise serializers.ValidationError({"End Date":"Start Date cannot be greater than End Date"})
        del validated_data['ticket_start_date']
        del validated_data['expiry_date']
        validated_data['event_id'] = self.context['event_id']
        validated_data['ticket_start_date'] = self.context['ticket_start_date']
        validated_data['expiry_date'] = self.context['expiry_date']
        validated_data['qty_left'] = self.context['qty_left']
        validated_data['ercess_fee'] = self.context['ercess_fee']
        validated_data['transaction_fee'] = self.context['transaction_fee']
        validated_data['active'] = 1
        return validated_data

    def ticketqtyidate(self, validated_data, *args, **kwargs):
        print("this is ticket qty validation")
        minticket = validated_data.get('min_qty')
        maxticket = validated_data.get('max_qty')
        if minticket > maxticket:
            raise serializers.ValidationError({"Ticket":"Min ticket cannot be greater than Max ticket"})
        return validated_ticketdata


class CategoriesSerialzier(serializers.ModelSerializer):
	class Meta:
		model = Categories
		fields = '__all__'

class TopicsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Topics
		fields = '__all__'