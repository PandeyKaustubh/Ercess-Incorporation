import hashlib
import datetime
from rest_framework import serializers

import re
from dashboard.models import Articles2, CategorizedEvents, StatusPromotionTicketing, Tickets, BankDetails, Stall, StallFacilities, StallUpload
from django.utils import timezone


class StallUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = StallUpload
        exclude = ['event_id']

    img = serializers.ImageField(
        use_url=True,
        required=False
    )
    file = serializers.FileField(
        use_url=True,
        required=False
    )


class FacilitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StallFacilities
        exclude = ['event_id']


class StallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stall
        exclude = ['event_id']

    stall_name = serializers.CharField(
        max_length=254,
        style={
            'autofocus': True,
            'template': 'stall/step_3/stall_name.html',
        },
    )
    total_quantity = serializers.IntegerField(

        style={
            'autofocus': True,
            'template': 'stall/step_3/total_quantity.html',
        },
    )

    booking_start_date = serializers.DateField(
        input_formats=['%d/%m/%Y', ],
        style={
            'template': 'stall/step_3/startdate.html'}
    )

    booking_start_time = serializers.TimeField(
        input_formats=['%I:%M %p'],
        style={
            'template': 'stall/step_3/stime.html'}
    )

    booking_end_date = serializers.DateField(
        input_formats=['%d/%m/%Y', ],
        style={
            'template': 'stall/step_3/enddate.html'}
    )
    booking_end_time = serializers.TimeField(
        input_formats=['%I:%M %p'],
        style={
            'template': 'stall/step_3/etime.html'}
    )
    full_stall_price = serializers.DecimalField(
        max_digits=20,
        decimal_places=3,
        style={
            'autofocus': True,
            'template': 'stall/step_3/full_stall_price.html',
        },
    )
    half_stall_price = serializers.DecimalField(
        max_digits=20,
        decimal_places=3,
        style={
            'autofocus': True,
            'template': 'stall/step_3/half_stall_price.html',
        },
    )
    number_of_chairs = serializers.IntegerField(

        style={
            'autofocus': True,
            'template': 'stall/step_3/number_of_chairs.html',
        },
    )
    counter = serializers.BooleanField(

        style={
            'autofocus': True,
            'template': 'stall/step_3/counter.html',
        },
    )
    any_condition = serializers.CharField(
        max_length=300,
        style={
            'autofocus': True,
            'template': 'stall/step_3/any_condition.html',
        },
    )
    size_in_meters = serializers.CharField(
        max_length=254,
        style={
            'autofocus': True,
            'template': 'stall/step_3/size_in_meters.html',
        },
    )



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
    sdate =serializers.DateField(
                        input_formats=['%d/%m/%Y',],
                        style={
                          'template': 'dashboard/create-event/step_1/startdate.html'}                      
                        )

    start_time =serializers.TimeField(
                        input_formats=['%I:%M %p'],
                        style={
                          'template': 'dashboard/create-event/step_1/stime.html'}
                        )
    edate =serializers.DateField(
                        initial=datetime.date.today,
                        input_formats=['%d/%m/%Y',],
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


class StatusPromotionTicketingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusPromotionTicketing
        fields = ['event_id','unique_id','mode','private','event_active','approval',
                  'network_share','ticketing', 'promotion', 'connected_user', 'complete_details']

#tickets serializer
class TicketsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tickets
        fields = ['ticket_name','ticket_price','other_charges','other_charges_type',
                  'ticket_qty','min_qty','max_qty','start_date','start_time_step5',
                  'end_date','end_time_step5',
#'ticket_start_date','expiry_date','ticket_msg',
                  'ticket_msg','ticket_label',
        #  Note : ercessfee and transaction fee must be calculated and then passed to the serializer
        # 'event_id','qty_left','ercess_fee','transaction_fee','active',
         ]
        
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
    start_date =serializers.DateField(
                         input_formats=['%d/%m/%Y',],
                         style={
                           'template': 'dashboard/create-event/step_5/startdate.html'}                      
                         )

    start_time_step5 =serializers.TimeField(
                         input_formats=['%I:%M %p'],
                         style={
                           'template': 'dashboard/create-event/step_5/stime.html'}
                         )
    end_date =serializers.DateField(
                         input_formats=['%d/%m/%Y',],
                         style={
                           'template': 'dashboard/create-event/step_5/enddate.html'}
                         )

   
    
    end_time_step5 =serializers.TimeField(
                         input_formats=['%I:%M %p'],
                         style={
                           'template': 'dashboard/create-event/step_5/etime.html'}
                         )
    
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
        sDate = validated_data.get('start_date')
        eDate = validated_data.get('end_date')
        print(sDate)
        print(eDate)
        if sDate > eDate:
            raise serializers.ValidationError({"End Date":"Start Date cannot be greater than End Date"})
        del validated_data['start_date']
        del validated_data['start_time_step5']
        del validated_data['end_date']
        del validated_data['end_time_step5']
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


class BankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetails
        fields = ['bank_name','ac_holder_name','ac_type','ac_number','ifsc_code','branch','gst_number' ]

    bank_name = serializers.CharField(
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/bankname.html',
                },
            )
    
    
    ac_holder_name = serializers.CharField(
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/accholdername.html',
                },
            )
    ac_type = serializers.CharField(
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/acctype.html',
                },
            )

    ac_number = serializers.CharField(
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/accno.html',
                },
    )
    
    ifsc_code = serializers.CharField(
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/ifsc.html',
                },
            )       


    branch = serializers.CharField(
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/branch.html',
                },
            ) 
    gst_number = serializers.CharField(required=False,
                max_length=20,
                style={
                    'autofocus': True,
                    'template': 'dashboard/bank-details-templates/gst.html',
                },
            )
    def validate(self, validated_data, *args, **kwargs):
        ifsc = validated_data.get('ifsc_code')
        acno = validated_data.get('ac_number')
        reg1='^[A-Za-z]{4}[a-zA-Z0-9]{7}$'
        reg2='^\d{9,18}$'
        validated_data['user_id']=self.context['user_id']
        #if (not re.match(reg1,ifsc)):
        #   raise serializers.ValidationError({"IFSC Code should have first 4 characters as digit and remaining 7 characters as alphanumeric"})
        if (not re.match(reg2,acno)):
            raise serializers.ValidationError({"Bank Account No should be between 9 to 18 digits"})
        return validated_data
            
            
