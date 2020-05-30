from django.urls import path
from admin_panel import views 
from admin_panel.views import AdminFeedBackList , AdminExpectationList
app_name = 'admin-panel'

urlpatterns =[
    path('',views.admin_home,name = 'home'),
    #path('edit/<int:event_id>',views.editButton,name='edit'),
    path('event-lists/',views.eventList,name='eve_list'),
    path('past-event-lists/',views.pastEventList,name='past_list'),
    path('date-range-event-lists/',views.dateRangeEventList,name='date_range_list'),
    path('created-range-event-lists/',views.createdDateRangeEventList,name='created_range_list'),
    path('started-range-event-lists/',views.startedDateRangeEventList,name='started_range_list'),
    path('event-details/<int:event_id>',views.EventDetailView.as_view(),name='details'),
    path('event-promotion-upcoming/',views.promotionUpcoming,name='up_prom'),
    path('event-promotion-past/',views.promotionPast,name='past_prom'),
    path('login/',views.admin_login,name = 'admin_login'),
    path('partner-sites/', views.partner_sites, name = 'test'),
    path('user-detail/', views.user_detail, name = 'user-detail'),
    path('display_user_event/<int:user_id>', views.display_user_event, name = 'display_user_event'),
    # path('add-rsvp/<int:event_id>', views.add_rsvp, name = 'add-rsvp'),
    path('add-sales/<int:event_id>', views.add_sales, name='add-sales'),

    path('sale-settled/', views.sale_settled.as_view(), name ='sale-settled'),
    path('sale-pending/',views.sale_pending.as_view(),name = 'sale-pending'),
    path('sale-list/', views.sale_settled.as_view(), name ='sale-list'),
    path('email-marketing/',views.email_marketing.as_view(),name = 'email-marketing'),
    path('email-marketing/<int:id>',views.email_marketing_detail,name = 'email-marketing_detail'),
    path('sms-marketing/',views.sms_marketing.as_view(),name = 'sms-marketing'),
    path('sms-marketing/<int:id>',views.sms_marketing_detail,name = 'sms-marketing_detail'),
    path('leads/',views.leads.as_view(),name = 'leads'),

    path('sale-list/<int:table_id>', views.sale_details, name='sale-details'), 

    path('payment-settlement/<str:booking_id>',views.payment_settlement,name='payment-settlement'),
    path('booking_details/<str:booking_id>',views.booking_details,name='booking-details'),
    # path('sale-list/edit/<int:table_id>', views.edit_sales, name='sale-edit'),
    # path('sale-settled-edit/<int:pk>', views.Sale_Edit.as_view(), name='sale-details')
    path('sale-list/<int:table_id>', views.sale_details, name='sale-details'),
    path('sale-list/<str:booking_id>',views.booking_details,name='booking-details'),
    path('details-partner/<int:table_id>',views.partner_site_details,name='details-page'),
    path('details-promotion-status/<int:table_id>',views.details_promotion_status,name='details-promotion-status'),
    # path('adduser/',views.UserRegister.as_view(),name = 'add'),
    # @author Shubham
    path('add-rsvp-details/<int:event_id>', views.add_rsvp_details, name = 'add-rsvp-details'),
    path('add-sales-free-tkt-details/<int:event_id>', views.add_sales_free_tkt_details, name = 'add-sales-free-tkt-details'),
    path('send-confirm-org-email/', views.send_confirm_org_email, name = 'send-confirm-org-email'),
    path('update-ticket-url/', views.update_ticket_url, name = 'update-ticket-url'),
    path('change-event-status/', views.change_event_status, name = 'change-event-status'),
    path('create-leads-csv', views.create_leads_csv, name = 'create-leads-csv'),

    path('feed-back-list/<int:event_id>', AdminFeedBackList.as_view(), name ='admin_feed_back_list'),
    path('feed-expectation-list/<int:event_id>', AdminExpectationList.as_view(), name ='admin_expectationlist'),
    path('add-edit-promotion-link/<int:event_id>',views.addEditPromotionLinks,name='add-edit-promotion-link')
    # ends here ~ @author Shubham 
]
