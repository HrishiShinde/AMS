import time
from django.shortcuts import redirect, render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Request, Timings, User

import datetime,csv, pytz
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

def checkMissedClocksPC(request):
    # time.sleep(30)
    date = datetime.date.today()
    userId = request.session['userId']
    try:
        db = Timings.objects.get(date = date, usrId = userId)
        data = {
            "success" : "Success"
        }
        return JsonResponse(data)
    except:
        data = {
            "fail" : "You haven't Clocked In Yet!"
        }
        return JsonResponse(data)

def doLogin(request):
    if request.method == "POST":
        userID = request.POST.get("userid")
        userPass = request.POST.get("pass")

        if userID == "admin" and userPass == "admin":
            request.session['user'] = userID
            userDb = User.objects.values()
            # print(userDb)
            return render(request, "adminUsers.html", {"success" : "Welcome " + userID, "data" : userDb})

        try:
            db = User.objects.get(userId = userID)
        except:
            return render(request, "login.html", {"fail" : "User-Id Incorrect"})
        if db.userPass == userPass:
            request.session['user'] = db.userName
            request.session['userId'] = userID

            date = datetime.date.today()
            db = User.objects.get(userId = userID)
            db.date = date
            db.hasLoggedIn = True
            db.save()

            return render(request, "index.html", {"success" : "Welcome " + db.userName})
        return render(request, "login.html", {"fail" : "Password Incorrect"})

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
        db = User.objects.get(userId = request.session['userId'])
        db.date = "-"
        db.hasLoggedIn = False
        db.hasClockedIn = False
        db.save()
        del request.session['user']
        try:
            del request.session['userId']
            try:
                del request.session['clkInToday']
                del request.session['clkedInToday']
                del request.session['clkedOutToday']
                del request.session['brkInToday']
                del request.session['brkOutToday']
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
        IST = pytz.timezone('Asia/Kolkata')
        timeNow = datetime.datetime.now(IST)
        dateToday = datetime.date.today()
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
        db = Timings.objects.create(usrId = uId, date = date, userClkIn = clkIn, status = status)
        db.save()
        db = User.objects.get(userId = uId, date = dateToday)
        db.hasClockedIn = True
        db.save()
        request.session['clkInToday'] = clkIn
        request.session['clkedInToday'] = "True"
        data = {
            "success" : "Clocked In!"
        }
        return JsonResponse(data)

@csrf_exempt
def clockOut(request):
    if request.method == "POST":
        clkIn = request.session['clkInToday']

        IST = pytz.timezone('Asia/Kolkata')

        listl = ((clkIn.replace(":"," ")).replace("-" , " ")).split()
        list2 = ((str(datetime.date.today()).replace("-" , " "))).split()
        year = int(list2[0])
        month = int(list2[1])
        day = int(list2[2])
        hour = int(listl[0])
        minu = int(listl[1])
        sec = int(listl[2])


        inTime = datetime.datetime(year,month,day,hour,minu,sec)

        timeNowUTC = datetime.datetime.now()
        timeNow = datetime.datetime.now(IST)
        # date = timeNow.strftime("%Y-%m-%d")
        inTimeRefined = inTime.strftime("%Y-%m-%d %H:%M:%S")
        L1 = ((inTimeRefined.replace(":"," ")).replace("-" , " ")).split()
        inTimeRefined = datetime.datetime(int(L1[0]),int(L1[1]),int(L1[2]),int(L1[3]),int(L1[4]),int(L1[5]))
        timeNowRefined = timeNow.strftime("%Y-%m-%d %H:%M:%S")
        L2 = ((timeNowRefined.replace(":"," ")).replace("-" , " ")).split()
        timeNowRefined = datetime.datetime(int(L2[0]),int(L2[1]),int(L2[2]),int(L2[3]),int(L2[4]),int(L2[5]))
        clkOut = timeNow.strftime("%H:%M:%S")

        print(inTimeRefined, timeNowRefined, type(inTimeRefined), type(timeNowRefined))

        out = timeNow.strftime("%H:%M")
        strOut = int(str(out)[0:2])

        overtime = False

        if 23 >= strOut > 18:
            overtime = True

        minususu = str(timeNowRefined - inTimeRefined)[0:5]
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

        request.session['clkedOutToday'] = "True"
        return JsonResponse(data)

@csrf_exempt
def brkIn(request):
    if request.method == "POST":
        clkIn = request.session['clkInToday']
        IST = pytz.timezone('Asia/Kolkata')
        timeNow = datetime.datetime.now(IST)
        brkIn = timeNow.strftime("%H:%M:%S")
        db = Timings.objects.get(userClkIn = clkIn)
        db.userBrkIn = brkIn
        db.save()
        data = {
            "success" : "Break In Recorded!"
        }
        request.session['brkInToday'] = "True"
        return JsonResponse(data)

@csrf_exempt
def brkOut(request):
    if request.method == "POST":
        clkIn = request.session['clkInToday']
        IST = pytz.timezone('Asia/Kolkata')
        timeNow = datetime.datetime.now(IST)
        brkOut = timeNow.strftime("%H:%M:%S")
        db = Timings.objects.get(userClkIn = clkIn)
        db.userBrkOut = brkOut
        db.save()
        data = {
            "success" : "Break Out Recorded!"
        }
        request.session['brkOutToday'] = "True"
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
                db = Timings.objects.create(usrId = usrId, date = date, hasLeaveAppointed = true, status = "Leave")
                db.save()
            elif types == "Half day":
                db = Timings.objects.create(usrId = usrId, date = date, hasHalfDayAppointed = true, status = "Half Day")
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

    for t in Timings.objects.values_list('timeId', 'usrId', 'userClkIn', 'userClkOut', 'userBrkIn', 'userBrkOut', 'status', 'hasHalfDayAppointed', 'hasLeaveAppointed', 'overtime', 'numOfHours'):
        writer.writerow(t)

    response['Content-Disposition'] = 'attachment; filename="attendence.csv"'
    return response

def add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        pwd = request.POST.get("pass")

        db = User.objects.create(userName = name, userPass = pwd)
        db.save()

        return redirect('/users')

def delete(request):
    if request.method == "POST":
        id = request.POST.get("id")

        db = User.objects.get(userId = id)
        db.delete()

        return redirect('/users')
