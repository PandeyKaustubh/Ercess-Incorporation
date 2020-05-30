from django.urls import path, include
from . import views as api_views
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
urlpatterns = [
    path('v1/signup',api_views.SignUp.as_view(),name='SignUp'),
    path('v1/verification_email',api_views.VerificationMail.as_view(),name='Verfication-Email'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
