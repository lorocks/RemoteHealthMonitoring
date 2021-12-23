from django.db import models
from django.conf import settings

# Create your models here.
class UserType(models.Model):
    Type = [("D", "Doctor"), ("P", "Patient")]
    userID = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    username = models.CharField(max_length = 4, primary_key = True)
    userType = models.CharField(max_length = 1, choices = Type, null = False)

    def __str__(self):
        return f"{self.username} of Django userID {self.userID}, {self.userType}"

class UserIDs(models.Model):
    username = models.ForeignKey(UserType, on_delete = models.CASCADE)

    def __str__(self):
        return self.username

class Doctors(models.Model):
    DoctorID = models.ForeignKey(UserIDs, on_delete = models.CASCADE, primary_key = True)
    Name = models.CharField(max_length = 100, null = False, blank = False)
    ContactNum = models.CharField(max_length = 12, null = False, blank = False) #do num validation in front end, add on_delete
    Hospital = models.CharField(max_length = 100, null = False, blank = False)

    def __str__(self):
        return f"{self.DoctorID.username}, {self.Name}"

class Patients(models.Model):
    GenderChoices = [("F", "Female"), ("M", "Male")]
    PatientID = models.ForeignKey(UserIDs, on_delete = models.CASCADE, primary_key = True)
    DoctorID = models.ForeignKey(Doctors, on_delete = models.CASCADE, null = False, blank = False)
    Name = models.CharField(max_length=100, null=False, blank=False)
    DOB = models.DateField(null=False, blank=False)
    Gender = models.CharField(max_length = 1, choices = GenderChoices)
    Address = models.CharField(max_length = 150, null=False, blank=False)
    ContactNum = models.CharField(max_length = 12, null = False, blank = False)
    EmergencyContact = models.CharField(max_length = 12, null = False, blank = False)
    Insurance = models.CharField(max_length = 50)
    EmailID = models.CharField(max_length = 100)

    def __str__(self):
        return f"{self.PatientID.username}, {self.Name}"


class DailyData(models.Model):
    PatientID = models.ForeignKey(Patients, on_delete = models.CASCADE)
    Date = models.DateField(null=False, blank=False)
    LastAvgTemp = models.FloatField()    #fill when person enters sugar lvl, by run procedure ig
    LastAvgHeartRate = models.FloatField()   #fill when person enters sugar lvl, by run procedure ig of previous day
    BloodSugar = models.FloatField()
    BloodPressure = models.FloatField()

    def __str__(self):
        return f"{self.PatientID}, {self.Date}"
#gotta run procedure for auto delete ig
class SecondlyData(models.Model):
    PatientID = models.ForeignKey(Patients, on_delete = models.CASCADE)
    Date = models.DateField(null=False, blank=False)
    Time = models.TimeField(null=False, blank=False)
    Pulse = models.FloatField(null=False, blank=False)
    Temp = models.FloatField(null=False, blank=False)

    def __str__(self):
        return f"{self.PatientID}, {self.Date}"

class WeeklyData(models.Model): # or monthly idk
    PatientID = models.ForeignKey(Patients, on_delete=models.CASCADE)
    Date = models.DateField(null=False, blank=False)
    Weight = models.FloatField()
    Height = models.FloatField()
    BMI = models.FloatField()

    def __str__(self):
        return f"{self.PatientID}, {self.Date}"