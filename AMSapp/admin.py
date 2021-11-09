from django.contrib import admin
from .models import Request, Timings, User

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['userId', 'userName', 'userPass']

@admin.register(Timings)
class TimingsAdmin(admin.ModelAdmin):
    list_display = ["timeId", "usrId", "date"
, "userClkIn"
, "userClkOut"
, "userBrkIn"
, "userBrkOut"
, "status"
, "hasHalfDayAppointed"
, "hasLeaveAppointed"
, "overtime"
, "numOfHours"]

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ['reqId', 'userID', 'type', 'date', 'reason', 'status', "approved"]

