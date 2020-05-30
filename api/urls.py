from django.urls import path, include
from . import views as api_views
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
urlpatterns = [

    path('v1/ticket-details',api_views.TicketDetails.as_view(),name='Ticket-Details'),

    path('v1/events_in/<str:cityname>/<str:state>',api_views.CityEventListing.as_view(),name='City-Events-Listing'),

    path('v1/categories/',api_views.CategoryList.as_view(),name='Categories-List'),

    path('v1/<str:categoryname>-events/', api_views.CategoryEventsListing.as_view(), name='Categorywise-Events'),

    path('v1/<str:event_name>/<int:event_id>',api_views.EventDetailView.as_view(),name='Event-Detail-View'),

    path('v1/online/',api_views.OnlineEventListing.as_view(),name='Online-Event-Listing'),

    path('v1/online/<str:categoryname>/',api_views.OnlineCategoryEventListing.as_view(),name='Online-Category-Event-Listing'),

    path('v1/booking/<str:source>/<str:event_id>',api_views.Booking.as_view(),name='Ticket-Booking'),

    path('v1/checkout',api_views.Checkout.as_view(),name='checkout'),

    path('v1/free-checkout',api_views.FreeCheckout.as_view(),name='free-checkout'),

    path('v1/<str:categoryname>/<str:subcategoryname>',api_views.SubCategoryEventListing.as_view(),name='subcategory-list'),

    path('v1/attendeeform/',api_views.EventAttendeeForm.as_view(),name='Attendee-Form'),

    path('v1/freeattendeeform/',api_views.FreeEventAttendeeForm.as_view(),name='Free-Event-Attendee-Form')
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
