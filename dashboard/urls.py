from django.urls import path, include
from django.conf.urls import  url
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.views.generic import TemplateView, View

from Ercesscorp.third_party_security import smartlogin
from Ercesscorp import views

from Ercesscorp.views import edit_event,step_three,edit_event_two,edit_event_four,edit_event_five,edit_action_four,edit_action_four,edit_action_five,new_ticket,UpdateStatus
from dashboard.views import  getHow, change_password ,UpdateUserInfo ,ExpectationList, FeedBackList, UploadCSV  #, third_step#,photo_list ,fourth_step

from dashboard.api.views import StallCreateAPIView, FacilitiesAPIView, StallUploadAPIView, StallUpdateAPIView, \
    EventSuccessView, FacilitiesUpdate, StallUploadUpdateAPIView

from dashboard.api import views as api_views

from .views import  EditDetailView


app_name = 'dashboard'

urlpatterns = [
    url(r'^$', getHow, name='how'),

    path('create-stall-step1/<int:event_id>/', api_views.FacilitiesAPIView.as_view(), name='facilities'),
    path('create-stall-step2/<int:event_id>/',api_views.StallUploadAPIView.as_view(), name='stall_upload'),
    path('create-stalls/<int:event_id>/', api_views.StallCreateAPIView.as_view(), name='create_stall'),
    path('update-stalls/<int:event_id>/', api_views.StallUpdateAPIView.as_view(), name='stall_update'),
    path('update-stall-step1/<int:event_id>/', api_views.FacilitiesUpdate.as_view(), name='facilities_update'),
    path('update-stall-step2/<int:event_id>/', api_views.StallUploadUpdateAPIView.as_view(), name='uploads_update'),

    path('add-event', api_views.ArticlesCreateAPIView.as_view(), name="step_one"),
    path('add-event-types/<str:md5>/<int:event_id>', api_views.CategoryCreateAPIView.as_view(), name="step_two"),
    path('add-event-images/<str:md5>/<int:event_id>', views.step_three, name="step_three"),
    path('update_info', UpdateUserInfo.as_view(), name='update_info'),
   
    path('expectation_list/<int:event_id>', ExpectationList.as_view(), name='expectation_list'),
    path('feed_back_list/<int:event_id>', FeedBackList.as_view(), name='feed_back_list'),
    path('upload-csv/<int:event_id>', UploadCSV.as_view(), name='upload_csv'),
    # path('upload-expectation-csv/<int:event_id>', UploadExpectationCSV.as_view(), name='upload_expectation_csv'),

    # path('add-event-images-action/<str:md5>/<int:event_id>', views.step_three_action, name="step_three_action"),
    path('ajax/topics', api_views.TopicsListAPIView.as_view()),
    path('add-event-description/<str:md5>/<int:event_id>', api_views.DescriptionCreateAPIView.as_view(), name="step_four"),
    path('add-event-tickets/<str:md5>/<int:event_id>', api_views.CreateTicketsView.as_view(), name="step_five"),
    path('add-event-question/<str:md5>/<int:event_id>', api_views.QuestionCreateAPIView.as_view(), name="step_six"),
    path('stall_added/', TemplateView.as_view(template_name='stall/stall_success.html'), name='stall_added'),
    path('event_added/<int:event_id>/', EventSuccessView.as_view(), name='event_added'),
    path('RSVP',views.RSVP,name='leads'),
    path('updateContact/',views.updateMobileNo, name="updateContact"),
    path('rsvp/<int:event_id>',views.rsvp_event,name='rsvp-event'),
    path('organizer_dashboard',views.manageevents, name='organizer-dashboard'),
    path('event-details/<int:event_id>',views.event_details, name='event-details'),
    path('sales', views.getSales, name='sales'),
    path('sales_details/<int:event_id>/',views.getSalesDetails, name ='sale_details'),
    path('inquiries', views.getInquiries, name='inquiries'),
    path('help',views.getHelp,name='help'),
    path('profile',views.profile,name='profile'),
    path('settings', change_password,name='settings'),
    path('organizer-agreement',views.organizer_agreement,name='organizer-agreement'),
    path('bank-details',api_views.BankDetailsView.as_view(), name="bank_details"),
    # path('create-stalls',views.create_stall, name="create_stall"),
    path('edit-event/<int:event_id>', EditDetailView.as_view(), name="detail"),
    path('boost-event/<int:event_id>', views.boost, name="boost-event"),
    path('edit-event/basic/<int:event_id>',views.edit_event, name='edit-event'),
    path('edit-event-two/<int:event_id>',views.edit_event_two, name='edit-event-two'),
    # path('edit-event-three/<int:event_id>',views.edit_event_three, name='edit-event-three'),
    path('edit-event-four/<int:event_id>',views.edit_event_four, name='edit-event-four'),
    path('edit-event-five/<int:event_id>/<int:ticket_id>',views.edit_event_five, name='edit-event-five'),
    path('edit_event_ticket/<event_id>',views.edit_event_ticket, name='edit-event-ticket'),
    path('new_ticket/<int:event_id>',views.new_ticket, name='new-ticket'),
    path('edit_action_two/<event_id>',views.edit_action_two, name='edit-action-two'),
    path('edit_action_five/<event_id>/<int:ticket_id>',views.edit_action_five, name='edit-action-five'),
    path('edit_action_four/<event_id>',views.edit_action_four, name='edit-action-four'),
    path('delete_ticket/<str:md5>/<int:event_id>/<int:ticket_id>/<int:return_page>',views.delete_ticket, name='delete-ticket'),
    path('update_event_tickets/<str:md5>/<int:event_id>/<int:ticket_id>',views.update_event_tickets, name='update-event-tickets'),
    path('edit_event_three/<int:event_id>',views.edit_event_three, name='edit-event-three'),
    path('edit-bank-details',api_views.EditBankDetailsView.as_view(), name="edit_bank_details"),

    path('update-event-status/<int:event_id>', UpdateStatus.as_view(), name="update_event_status"),
    # path('unlock-rsvp/<int:event_id>/<int:table_id_par>',views.unlock_rsvp,name='unlock-rsvp'),
    # path('subscribe-premium-package/<int:event_id>/<int:table_id_par>/<charges_id_par>',views.subscribe_premium_package,name='subscribe-premium-package'),
    # path('payment-success-rsvp',views.payment_success_rsvp,name='payment-success-rsvp'),
    # path('payment-fail-rsvp',views.payment_fail_rsvp,name='payment-fail-rsvp'),
    
    # urls for duplicate events
    path('duplicate-event-basics/<int:event_id>', views.duplicate_event_basics,name='duplicate-event-basics'),
    path('duplicate-event-two/<int:old_event_id>/<int:new_event_id>', views.duplicate_event_two,name='duplicate-event-two'),
    path('duplicate-event-three/<int:old_event_id>/<int:new_event_id>', views.duplicate_event_three,name='duplicate-event-three'),
    path('duplicate-event-four/<int:old_event_id>/<int:new_event_id>', views.duplicate_event_four,name='duplicate-event-four'),
    path('duplicate-event-five/<int:old_event_id>/<int:new_event_id>/<int:ticket_id>', views.duplicate_event_five,name='duplicate-event-five'),
    path('duplicate-event-tickets/<int:old_event_id>/<int:new_event_id>', views.duplicate_event_tickets,name='duplicate-event-tickets'),
    path('save-duplicate-event-five', views.save_duplicate_event_five,name='save-duplicate-event-five'),
    path('duplicate-new-ticket/<int:old_event_id>/<int:new_event_id>', views.duplicate_new_ticket,name='duplicate-new-ticket'),
    path('duplicate-event-six/<int:old_event_id>/<int:new_event_id>', views.duplicate_event_six,name='duplicate-event-six'),
    # ends here ~ urls for duplicate events

    path('check-event-already-created', views.check_event_already_created,name='check-event-already-created'),
    path('check-event-already-created-edit', views.check_event_already_created_edit,name='check-event-already-created-edit'),
    path('update-ann-access-table', views.updateAnnAccessTable,name='update-ann-access-table'),
    path('show-rsvp-premium-packages/<int:event_id>/<str:service_type>/<str:purpose_of_payment>',views.show_rsvp_premium_packages,name='show-rsvp-premium-packages'),
    
    # urls for payment package
    #IMPORTANT NOTE (For PAYUMONEY PAYMENT GATEWAY): All parameter name which start wifh udf's, that is temporary because we don't know about next values.. must need to change in future if include more values (e.g, now, udf2=event_id and udf3=charges_id) & MAX 10 UDF is allowed by PayUMoney
    path('buy-premium-package/<int:event_id>/<int:charges_id>/<int:udf4>/<int:udf5>/<str:purpose_of_payment>',views.buy_premium_package,name='buy-premium-package'),
    path('package-payment-success',views.package_payment_success,name='package-payment-success'),
    path('package-payment-fail',views.package_payment_fail,name='package-payment-fail'),
    # ends here ~ urls for payment package

    # sms marketing urls
    path('sms-marketing-checklist/<int:event_id>',views.sms_marketing_checklist,name='sms-marketing-checklist'),

    path('sms-campaign-listing/<int:event_id>',views.sms_campaign_listing,name='sms-campaign-listing'),

    path('sms-marketing-initial-details/<int:event_id>',views.sms_marketing_initial_details,name='sms-marketing-initial-details'),
    path('sms-marketing-advance-details/<int:event_id>/<int:template_id>',views.sms_marketing_advance_details,name='sms-marketing-advance-details'),
    path('sms-marketing-advance-details-scheduling/<int:event_id>/<int:template_id>',views.sms_marketing_advance_details_scheduling,name='sms-marketing-advance-details-scheduling'),
    path('sms-marketing-success-page/<int:event_id>',views.sms_marketing_success_page,name='sms-marketing-success-page'),
    path('sms-marketing-schedule',views.sms_marketing_schedule,name='sms-marketing-schedule'),
    # ends here ~ sms marketing urls

    # email marketing urls

    path('email-marketing-checklist/<int:event_id>',views.email_marketing_checklist,name='email-marketing-checklist'),

    path('email-campaign-listing/<int:event_id>',views.email_campaign_listing,name='email-campaign-listing'),
    path('select-email-marketing-template/<int:event_id>',views.select_email_marketing_template,name='select-email-marketing-template'),
    path('email-marketing-initial-details/<int:event_id>/<str:template_name>',views.email_marketing_initial_details,name='email-marketing-initial-details'),


    path('email-marketing-advance-details/<int:event_id>/<int:campaign_template_id>',views.email_marketing_advance_details,name='email-marketing-advance-details'),
    path('email-marketing-advance-details-scheduling/<int:event_id>/<int:campaign_template_id>',views.email_marketing_advance_details_scheduling,name='email-marketing-advance-details-scheduling'),
    path('email-marketing-success-page/<int:event_id>/<int:campaign_template_id>',views.email_marketing_success_page,name='email-marketing-success-page'),
    path('email-marketing-schedule',views.email_marketing_schedule,name='email-marketing-schedule'),
    # ends here ~ email marketing urls

    path('toggle-referral-program/<int:event_id>',views.toggle_referral_program,name='toggle-referral-program'),
    path('affiliate-marketing/<int:event_id>',views.affiliate_marketing,name='affiliate-marketing'),
    path('add-more-credit/<int:event_id>/<str:purpose>',views.add_more_credit,name='add-more-credit'),
    path('content-distribution/<int:event_id>',views.content_distribution,name='content-distribution'),

    ############################# TicketSaga API's ############################################################

    path('/api/v1/home',api_views.Index.as_view(),name='index-api-view'),

    path('/api/v1/ticket-details',api_views.TicketDetails.as_view(),name='ticket-details-api-view'),

    path('api/v1/events_in/<str:cityname>/<str:state>',api_views.EventsIn.as_view(),name='events-in-api-view'),


    path('<str:categoryname>-events/', api_views.CategoryEventsList.as_view(), name='categorywise-events-api-view'),


]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

