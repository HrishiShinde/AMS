from django.contrib import admin
from .models import Request, Timing, User

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['userId', 'userName', 'userPass']

@admin.register(Timing)
class TimingsAdmin(admin.ModelAdmin):
    list_display = [ "usrId", "date"
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

