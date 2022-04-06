from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import *
from django.shortcuts import render
from django.urls import reverse
from datetime import *

from django.core.mail import send_mail

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import testingAPISerializer
from .models import testingAPI

# Create your views here.

def index(request):
    if not request.user.is_authenticated:
        return render(request,"login.html",{"message": None})
    current_user = request.user
    user_type = UserType.objects.filter(username = current_user.username)

    if len(user_type) > 0:
        user_type = user_type[0]
        if user_type.userType == "D":
            return HttpResponseRedirect(reverse("doctor_dashboard"))
        elif user_type.userType == "P":
            return HttpResponseRedirect(reverse("patient_dashboard"))
    else:
        message = {
            "message": "Logged in Yay"
        }
        return render(request, "index.html", message)

def logout_view(request):
    logout(request)
    return render(request,"login.html",{"message":"Logged out"})

def login_view(request):
    if request.method == 'POST':
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {"message": "Invalid credentials"})
    else:
        raise Http404("Invalid Gateway")

    #make all request post and put if request.method==post else raise http404("invalid")
def patient_dashboard_view(request):
    current_user = request.user
    user_type = UserType.objects.filter(username=current_user.username)
    user_type = user_type[0]

    actualWeekly = None

    if user_type.userType == 'D' and request.method == 'GET':
        return HttpResponseRedirect(reverse("index"))

    day = timedelta(1)
    message = {
        "message": "Logged in as Patient",
        "user": user_type,
        "details": None,
        "daily": None,
        "weekly": None,
        "secondPulData": [],
        "secondTempData": [],
        "timeData": []
    }

    if request.method == 'POST':
        patient_check = request.POST["docpost"]
        patients = Patients.objects.all()
        for thing in patients:
            if thing.PatientID.username == patient_check[:4]:
                patient = thing
        message["message"] = "Details Below"
    else:
        patient = Patients.objects.filter(PatientID=user_type.username)
        patient = patient[0]

    daily = DailyData.objects.filter(PatientID=patient, Date=datetime.now().date() - timedelta(1))
    if len(daily) > 0:
        daily = daily[len(daily)-1]
    secondly = SecondlyData.objects.filter(PatientID=patient, Date=datetime.now().date())
    weekly = WeeklyData.objects.filter(PatientID=patient)

    for thing in weekly:
        if thing.Date <= datetime.now().date() and thing.Date > datetime.now().date() - timedelta(7):
            actualWeekly = thing
    dos = 2
    for thing in secondly:
        message["secondPulData"].append(thing.Pulse)
        message["secondTempData"].append(thing.Temp)
        ts = thing.Time.hour * 3600 + thing.Time.minute * 60 + thing.Time.second
        message["timeData"].append(ts)
    message["secondPulData"] = message["secondPulData"][-90:]
    message["secondTempData"] = message["secondTempData"][-90:]
    message["timeData"] = message["timeData"][-90:]
    message["details"] = patient
    message["daily"] = daily
    message["weekly"] = actualWeekly
    return render(request, "patient.html", message)

def doctor_dashboard_view(request):
    current_user = request.user
    user_type = UserType.objects.filter(username=current_user.username)
    user_type = user_type[0]

    if user_type.userType == 'P':
        return HttpResponseRedirect(reverse("index"))

    doctor = Doctors.objects.filter(DoctorID=user_type.username)
    doctor = doctor[0]
    patients = Patients.objects.filter(DoctorID=doctor)

    message = {
        "message": "Logged in as Doctor",
        "user": doctor,
        "patients": patients
    }
    return render(request, "doctor.html", message)

def redirect_adddata_view(request):
    message = {
        "message": None,
        "details": request.POST["patient"]
    }
    if 'weekly' in request.POST:
        message["message"]="Enter the Weekly Data"
        return render(request, "weeklyadd.html", message)
    elif 'daily' in request.POST:
        message["message"]="Enter the Daily Data"
        return render(request, "dailyadd.html", message)
    else:
        raise Http404("Invalid brr Gateway")
# take value of button then redirect

# need to somehow pass patient ID for both
def add_weekly_view(request):
    if request.method == 'POST':
        patient_check = request.POST["patient"]
        patients = Patients.objects.all()
        for thing in patients:
            if thing.PatientID.username == patient_check[:4]:
                guy = thing
        weight = float(request.POST["weight"])
        height = float(request.POST["height"])
        date = datetime.now().date()
        bmi = weight*10000/(height*height)
        bmi = round(bmi, 3)
        weeklydata = WeeklyData(PatientID=guy, Date=date, Weight=weight, Height=height, BMI=bmi)
        weeklydata.save()
    else:
        raise Http404("Invalid brr Gateway")
    return HttpResponseRedirect(reverse("index"))

def add_daily_view(request):
    if request.method == 'POST':
        patient_check = request.POST["patient"]
        patients = Patients.objects.all()
        for thing in patients:
            if thing.PatientID.username == patient_check[:4]:
                guy = thing
        sugar = float(request.POST["sugar"])
        pressure = float(request.POST["pressure"])
        date = datetime.now().date() - timedelta(1)
        secondly_data = SecondlyData.objects.filter(PatientID=guy, Date=date)
        sum = pulse = temp = oxi = avg_pulse = avg_temp = avg_oxi = 0
        if len(secondly_data) > 0:
            for thing in secondly_data:
                sum += 1
                pulse += thing.Pulse
                oxi += thing.Oxygen
                temp += thing.Temp
            avg_pulse = pulse/sum
            avg_temp = temp/sum
            avg_oxi = oxi/sum
        dailydata = DailyData(PatientID=guy, Date=date, LastAvgTemp=avg_temp, LastAvgOxygen=avg_oxi, LastAvgHeartRate=avg_pulse, BloodSugar=sugar, BloodPressure=pressure)
        dailydata.save()
    else:
        raise Http404("Invalid brr Gateway")
    return HttpResponseRedirect(reverse("index"))

def redirect_notify(request):
    if request.method == 'POST':
        current_user = request.user
        user_type = UserType.objects.filter(username=current_user.username)
        user_type = user_type[0]
        if user_type.userType == 'P':
            patient = Patients.objects.filter(PatientID=user_type.username)
            patient = patient[0]
            send_mail('Appointment Request', f'Dear Doctor,\nI would like to request for an appointment\nRegards {current_user.username}', 'll753@live.mdx.ac.uk', [patient.DoctorID.EmailID], fail_silently=False)
            return HttpResponseRedirect(reverse("index"))
        else:
            message = {
                "details": request.POST["patient"]
            }
            return render(request, "notify.html", message)
    else:
        return Http404("Invalid brr Gateway")

def doctor_email(request):
    if request.method == 'POST':
        content = request.POST["message"]
        title = request.POST["title"]
        patient_check = request.POST["patient"]
        patients = Patients.objects.all()
        for thing in patients:
            if thing.PatientID.username == patient_check[:4]:
                guy = thing
        send_mail(title,
                  content,
                  'll753@live.mdx.ac.uk', [guy.EmailID], fail_silently=False)
        return HttpResponseRedirect(reverse("index"))
    return Http404("Invalid brr Gateway")


"""Weekly has to be added by patient and BMI directly calculated
Secondly is got full time from sensor
Daily
date in models is of type date from datetime lib 
"""

@api_view(['GET', 'POST'])
def http_api(request):
    if request.method == 'GET':
        snippets = testingAPI.objects.all()
        serializer = testingAPISerializer(snippets, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = testingAPISerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)