from django import db
from django.db import models

# Create your models here.
class User(models.Model):

    userId = models.AutoField(primary_key = True)
    userName = models.CharField(max_length=50)
    userPass = models.CharField(max_length=20)

    class Meta:
        db_table = "User"

class Timings(models.Model):

    timeId = models.AutoField(primary_key = True, default=0)
    usrId = models.IntegerField()
    date = models.CharField(max_length=50, default = "-")
    userClkIn= models.CharField(max_length=50, default="-")
    userClkOut = models.CharField(max_length=50, default="-")
    userBrkIn = models.CharField(max_length=50, default="-")
    userBrkOut = models.CharField(max_length=50, default="-")
    status = models.CharField(max_length=50, default="-") # Present, Absent, Late, Halfday, Early.
    hasHalfDayAppointed = models.BooleanField(default=False)
    hasLeaveAppointed = models.BooleanField(default=False)
    overtime  = models.BooleanField(default=False)
    numOfHours = models.CharField(max_length=50, default=0)

    class Meta:
        db_table = "Timings"

class Request(models.Model):
    
    reqId = models.AutoField(primary_key = True)
    userClkIn= models.CharField(max_length=50, default="-")
    userID = models.IntegerField()
    type = models.CharField(max_length=50)
    date = models.CharField(max_length=50)
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=50, default="Not yet")
    approved = models.BooleanField(default=False)

    class Meta:
        db_table = "Request"
