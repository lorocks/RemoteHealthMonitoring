from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("patient_dashboard", views.patient_dashboard_view, name="patient_dashboard"),
    path("doctor_dashboard", views.doctor_dashboard_view, name="doctor_dashboard")
]
