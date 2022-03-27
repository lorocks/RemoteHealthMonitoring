from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import *
from django.shortcuts import render
from django.urls import reverse
from datetime import *

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

    daily = DailyData.objects.filter(PatientID = patient, Date = datetime.now().date() - timedelta(1))
    daily = daily[len(daily)-1]
    # position = len(daily)-1
    # daily = daily[position]
    secondly = SecondlyData.objects.filter(PatientID=patient, Date = datetime.now().date())
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
        print(type(thing.Time.strftime("%H:%M:%S")))

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
    patients = Patients.objects.filter(DoctorID = doctor)

    message = {
        "message": "Logged in as Doctor",
        "user": doctor,
        "patients": patients
    }
    return render(request, "doctor.html", message)

"""Weekly has to be added by patient and BMI directly calculated
Secondly is got full time from sensor
Daily
date in models is of type date from datetime lib 
"""

def html_api(request):
    return