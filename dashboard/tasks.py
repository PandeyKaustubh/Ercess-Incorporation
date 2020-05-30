# main/tasks.py
import logging
from django.core.mail import send_mail,EmailMultiAlternatives,EmailMessage
from django.conf import settings
from Ercess.celery import app
# from datetime import datetime
import string,requests
from datetime import datetime,timedelta
import sys
from django.utils import timezone
from dashboard.models import *
from django.template.loader import render_to_string, get_template

@app.task
def add_message_link_mail():
    try:
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        get_upcoming_event = Articles2.objects.filter(sdate__contains = tomorrow)
        for i in get_upcoming_event:
            event_id = i.id
            check_booking = TicketsSale.objects.filter(event_id = event_id)
            for j in check_booking:
                booking_id = j.booking_id
                get_emails = ExpectationsFeedbacks.objects.filter(event_id = event_id, exp_email_attempts__lt = 3)
                for email in get_emails:
                    single_email = email.email
                    convert_email = str(single_email)
                    link = settings.BASE_URL+"/live/expectation/"+str(event_id) + '/' + str(booking_id)
                    content_html = render_to_string('static/common/exp_cronjob_mail.html', {'link':link})
                    message = ""
                    recipient_list = [convert_email]
                    email_from = settings.EMAIL_HOST_USER
                    subject = "For Expectation Message"
                    send_mail(subject,message,email_from, recipient_list, html_message = content_html)
                    email.exp_email_attempts = email.exp_email_attempts+1
                    email.exp_mail_status = "sent mail"
                    email.save()
               
                
    
        return True
    except Exception as e:
        raise e


@app.task
def add_feedback_message_link_mail():
    try:
        today = datetime.now().date()     
        get_today_event = Articles2.objects.filter(edate__contains = today)
        for i in get_today_event:
            event_id = i.id
            check_booking = TicketsSale.objects.filter(event_id = event_id)
            for j in check_booking:
                booking_id = j.booking_id
                get_emails = ExpectationsFeedbacks.objects.filter(event_id = event_id, feedback_mail_attempts__lt = 3)
                for email in get_emails:
                    single_email = email.email

                    convert_email = str(single_email)
                    
                    link = settings.BASE_URL+"/live/feed_back/"+str(event_id)+ '/' + str(booking_id)
                    content_html = render_to_string('static/common/feedback_cronjob_mail.html', {'link':link})
                    message = ""
                    recipient_list = [convert_email]
                    email_from = settings.EMAIL_HOST_USER
                    subject = "For FeedBack Message"
                    send_mail(subject,message,email_from, recipient_list, html_message = content_html)
                    email.feedback_mail_attempts = email.feedback_mail_attempts + 1
                    email.feedback_mail_status = "sent mail"
                    email.save()
    
        return True
    except Exception as e:
        raise e