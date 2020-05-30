"""Ercess URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""



from django.contrib import admin
from django.conf.urls import  url
from Ercesscorp import  views 
from api import views as api_views
from django.urls import  path ,re_path ,include
from django.conf import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from Ercesscorp.apiviews import *
from dashboard import url_shortner
from Ercesscorp.views  import   FeedBacks, Expectation
# from Ercesscorp.views import   UpdateUserInfo
# app_name = 'Ercess'
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/login/$',views.loginview ,name='login'),
    url(r'^live/dashboard/', include('dashboard.urls')),
    url(r'^$', views.home , name='home'),
    url(r'^api/',include('api.urls')),
    url(r'^ercess-api/',include('ercess_api.urls')),
   # url(r'^live/dashboard/organizer_dashboard',views.manageevents),
    url(r'^home/$', views.home, name='home'),
    url(r'^live/$',views.home , name='home'),
    url(r'^live/verify_email/(?P<slug>[\w-]+)/$', views.verify_mail),

    url(r'^admin-site/',include('admin_panel.urls')), 

    url(r'^live/login/$', views.loginview, name='login'),
    url(r'^live/logout/$', views.logoutview, name='logout'),
    url(r'^live/signup/$', views.registration,name='signup'),
    url(r'^live/multichannel/$',views.multichannelpromotion,name='multichannel-promotion'),
    url(r'^live/event-promotion/sms-marketing/$',views.smsMarketing,name='sms-marketing'),
    url(r'^live/event-promotion/email-marketing/$',views.emailMarketing,name='email-marketing'),
    url(r'^live/event-promotion/referral-program/$',views.referralProgram,name='referral-program'),
    url(r'^live/event-promotion/strategic-content-marketing/$',views.strategicContentMarketing,name='strategic-content-marketing'),
    url(r'^live/business-size/startup/$',views.startup,name='startup'),
    url(r'^live/business-size/enterprise/$',views.enterprise,name='enterprise'),
    url(r'^live/business-type/music-dance/$',views.musicDance,name='music-dance'),
    url(r'^live/business-type/entertainment/$',views.entertainment,name='entertainment'),
    url(r'^live/business-type/networking/$',views.networking,name='networking'),
    url(r'^live/business-type/learning/$',views.learning,name='learning'),
    url(r'^live/support/faq/$',views.faq,name='faq'),
    url(r'^live/support/knowledge-base/$',views.knowledgeBase,name='knowledge-base'),
    url(r'^live/about/vision-mission-values/$',views.visionMissionValues,name='vision-mission-values'),
    
    url(r'^live/sell-event-stalls/$',views.sellstallspaces, name='sell-event-stalls'),
    url(r'^live/paid-advertisement/$', views.advertisement,name='advertisement'),
    url(r'^live/how-it-works/$',views.howitworks, name='how-it-works'),
    url(r'^live/about/$',views.aboutus,name='about-us'),
    url(r'^live/contact/$',views.contactus,name='contact-us'),
    url(r'^live/blogs/$', views.blog, name='blog'),
    url(r'^live/blog-post/(?P<pk>[0-9]+)$', views.blogpost,name='blog-post'),
    url(r'^live/careers/$', views.career, name='careers'),
    url(r'^live/pricing/$', views.pricing, name='pricing'),
    url(r'^live/no-event-page/$', views.no_event_page, name='no_event_page'),

    path('live/feed_back/<int:event_id>/<str:booking_id>', FeedBacks.as_view(), name='feed_back'),  
    path('live/expectation/<int:event_id>/<str:booking_id>', Expectation.as_view(), name='expectation'),
    #    url(r'^live/verify_email/$', views.verify_mail, name='verify-email'),
    url(r'^live/forgot_password/$', views.forgotPassword, name='forgot-password'),
    url(r'^live/reset_password/(?P<slug>[\w-]+)/$', views.resetPassword),
    url(r'^live/set_new_password/$', views.setNewPassword),
    
#    url(r'^live/reset_password/$', views.resetPassword,name='reset-password'),


    url(r'^live/partners/$', views.partners, name='partners'),
    url(r'^live/privacy-policy/$', views.privacypolicy , name='privacy-policy'),
    url(r'^live/api/blogs/$' , BlogDetails.as_view(),name='blog-details'),
    url(r'^live/api/blogs/(?P<pk>[0-9]+)$', BlogSpecific.as_view(),name='blogspecific'),
    url(r'^live/api/users/$', Reg.as_view(),name='reg'),
    url(r'^live/api/login/$', LoginView.as_view(),'loginview'),
    url(r'^live/case-studies/$',views.case_studies, name='case-studies'),
    url(r'^live/cashback-info/(?P<slug>[\w-]+)$', views.provideCashbackDetails),
    url(r'^rcss/(?P<slug>[\w-]+)$', url_shortner.expand_url)


]

if settings.DEBUG:
    
    import debug_toolbar
    
    urlpatterns = [
      url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
