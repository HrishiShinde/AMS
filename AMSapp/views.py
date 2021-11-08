from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Request, Timings, User

import datetime,csv
from time import daylight, strftime

# Create your views here.
def renderLogin(request):
    return render(request, "login.html")

def renderHome(request):
    return render(request, "index.html")

def renderLeave(request):
    uId = request.session["userId"]
    reqDb = Request.objects.filter(userID = uId)
    return render(request, "leave.html", {"data" : reqDb})

def renderUsers(request):
    userDb = User.objects.values()
    return render(request, "adminUsers.html", {"data" : userDb})

def renderTimings(request):
    timeDb = Timings.objects.values()
    return render(request, "adminTime.html", {"data" : timeDb})

def renderRequest(request):
    reqDb = Request.objects.values()
    context = {"data" : reqDb}
    try:
        msg = request.session['msg']
        del request.session['msg']
        context = {"data" : reqDb, "success" : msg}
    except:
        print()
    return render(request, "adminRequest.html", context)

def doLogin(request):
    if request.method == "POST":
        userID = request.POST.get("userid")
        userPass = request.POST.get("pass")

        if userID == "admin" and userPass == "admin":
            request.session['user'] = userID
            userDb = User.objects.values()
            # print(userDb)
            return render(request, "adminUsers.html", {"success" : "Welcome " + userID, "data" : userDb})

        for u in User.objects.raw('select * from User where userId="%s"' % (userID)):
            if u.userPass == userPass:
                request.session['user'] = u.userName
                request.session['userId'] = userID
                return render(request, "index.html", {"success" : "Welcome " + u.userName})
            return render(request, "login.html", {"fail" : "Password Incorrect"})
        return render(request, "login.html", {"fail" : "User-Id Incorrect"})

def doRequest(request):
    if request.method == "POST":
        userID = request.POST.get("usrId")
        reqType = request.POST.get("type")
        date = request.POST.get("date")
        reason = request.POST.get("reason")

        print(userID, reqType, reason, date, type(date), "---------")
        reqDb = Request.objects.create(userID = userID, type = reqType, date = date, reason = reason)
        reqDb.save()
        return render(request, "index.html", {"success" : "Requested successsfully"})

def doLogout(request):
    try:
        del request.session['user']
        try:
            del request.session['userId']
            try:
                del request.session['clkInToday']
            except:
                print("clkInToday Not present")
        except:
            print("userId Not present")
    except:
        print("User Not present")
    finally:    
        return render(request, "login.html", {"success" : "Logout successsful"})

@csrf_exempt
def clockIn(request):
    if request.method == "POST":
        uId = request.session['userId']
        timeNow = datetime.datetime.now()
        date = timeNow.strftime("%Y-%m-%d")
        clkIn = timeNow.strftime("%H:%M:%S")
        timeNow = int((timeNow.strftime("%H:%M")).replace(":",""))
        if int(timeNow) < 900:
            status = "Early"
        elif 900 < int(timeNow) < 930:
            status = "Present"
        elif 930 < int(timeNow) < 1200:
            status = "Late"
        elif int(timeNow) > 1200:
            status = "Half Day"
        # print("========", clkIn, type(clkIn), "======")
        # print("========", timeNow, type(timeNow), status, "======")
        db = Timings.objects.create(userId = uId, date = date, userClkIn = clkIn, status = status)
        db.save()
        request.session['clkInToday'] = clkIn
        data = {
            "success" : "Clocked In!"
        }
        return JsonResponse(data)

@csrf_exempt
def clockOut(request):
    if request.method == "POST":
        clkIn = request.session['clkInToday']
        listl = ((clkIn.replace(":"," ")).replace("-" , " ")).split()
        year = int(listl[0])
        month = int(listl[1])
        day = int(listl[2])
        hour = int(listl[3])
        minu = int(listl[4])
        sec = int(listl[5])
        inTime = datetime.datetime(year,month,day,hour,minu,sec)

        timeNow = datetime.datetime.now()
        clkOut = timeNow.strftime("%Y-%m-%d %H:%M:%S")

        # inTime = inTime.strftime("%H:%M")
        out = timeNow.strftime("%H:%M")
        strOut = int(str(out)[0:2])

        if 23 > strOut > 18:
            overtime = True

        minususu = str(timeNow - inTime)[0:5]
        if minususu[-1] == ":":
            minususu = minususu[:-1]
        # print(minususu)
        # print("========", clkOut, type(clkOut), "======")    2021-11-05 20:45:47
        db = Timings.objects.get(userClkIn = clkIn)
        db.userClkOut = clkOut
        db.overtime = overtime
        db.numOfHours = minususu
        db.save()
        data = {
            "success" : "Clocked Out!"
        }
        return JsonResponse(data)

@csrf_exempt
def brkIn(request):
    if request.method == "POST":
        clkIn = request.session['clkInToday']
        timeNow = datetime.datetime.now()
        brkIn = timeNow.strftime("%Y-%m-%d %H:%M:%S")
        db = Timings.objects.get(userClkIn = clkIn)
        db.userBrkIn = brkIn
        db.save()
        data = {
            "success" : "Break In Recorded!"
        }
        return JsonResponse(data)

@csrf_exempt
def brkOut(request):
    if request.method == "POST":
        clkIn = request.session['clkInToday']
        timeNow = datetime.datetime.now()
        brkOut = timeNow.strftime("%Y-%m-%d %H:%M:%S")
        db = Timings.objects.get(userClkIn = clkIn)
        db.userBrkOut = brkOut
        db.save()
        data = {
            "success" : "Break Out Recorded!"
        }
        return JsonResponse(data)

@csrf_exempt
def status(request):
    if request.method == "POST":
        reqId = request.POST.get("id")
        usrId = request.POST.get("uid")
        date = request.POST.get("date")
        # clkIn = request.session['clkInToday']
        btn = request.POST.get("btn")
        types = request.POST.get("type")
        if btn == "Approve":
            status = "Approved"
            true = True
            if types == "Leave":
                db = Timings.objects.create(userId = usrId, date = date, hasLeaveAppointed = true, status = "Leave")
                db.save()
            elif types == "Half day":
                db = Timings.objects.create(userId = usrId, date = date, hasHalfDayAppointed = true, status = "Half Day")
                db.save()
        else:
            status = "Denied"
        print(reqId , "------", btn)
        db = Request.objects.get(reqId = reqId)
        db.status = status
        db.approved = True
        db.save()
        request.session["msg"] = status
        return redirect("/request")

def export(request):
    response = HttpResponse(content_type='text/csv')

    writer = csv.writer(response)
    writer.writerow(['timeId', 'userId', 'userClkIn', 'userClkOut', 'userBrkIn', 'userBrkOut', 'status', 'hasHalfDayAppointed', 'hasLeaveAppointed', 'overtime', 'numOfHours'])

    for t in Timings.objects.values_list('timeId', 'userId', 'userClkIn', 'userClkOut', 'userBrkIn', 'userBrkOut', 'status', 'hasHalfDayAppointed', 'hasLeaveAppointed', 'overtime', 'numOfHours'):
        writer.writerow(t)

    response['Content-Disposition'] = 'attachment; filename="attendence.csv"'
    return response
