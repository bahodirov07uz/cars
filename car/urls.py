from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "car"

urlpatterns = [
    path('',views.HomeView.as_view(),name="home"),
    path('car/<int:pk>/', views.CarDetailView.as_view(), name='car_detail'),

    path('thank-you/', views.ThankYouView.as_view(), name='thank_you'),

    path("contact/", views.ContactView.as_view(), name="contact"),
    path("contact/car/<int:car_id>/", views.ContactView.as_view(), name="contact_for_car"),
    path("about/",views.AboutPage.as_view(),name="about"),
    # path("finance/",views.FinanceView.as_view(),name="finance"),
    path("shipping/",views.ShippingView.as_view(),name="shipping"),
    path("privacy/",views.PrivacyView.as_view(),name="privacy"),
    path("terms-of-use/",views.TermsOfUseView.as_view(),name="termsofuse"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
