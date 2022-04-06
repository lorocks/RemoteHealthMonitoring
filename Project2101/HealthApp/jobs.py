from schedule import Scheduler
import threading
import time
import datetime
import random

from .models import *

def get_firebase_to_web():
    patient_check = "P001"
    patients = Patients.objects.all()
    for thing in patients:
        if thing.PatientID.username == patient_check:
            guy = thing
    secondly = SecondlyData(PatientID=guy,Date=datetime.datetime.now().date(),Time=datetime.datetime.now().time(),Pulse=60 + random.randint(0,40) + random.random(),Temp=random.random() + 36,Oxygen=99)
    secondly.save()

def delete_old_records():
    return

def run_continously(self, interval=2):
    cease_continous_run = threading.Event()

    class ScheduleThread(threading.Thread):

        @classmethod
        def run(cls):
            while not cease_continous_run.is_set():
                self.run_pending()
                time.sleep(interval)

    continous_thread = ScheduleThread()
    continous_thread.setDaemon(True)
    continous_thread.start()
    return cease_continous_run

Scheduler.run_continously = run_continously

def start_scheduler():
    scheduler = Scheduler()
    scheduler.every().second.do(get_firebase_to_web)
    scheduler.run_continously()