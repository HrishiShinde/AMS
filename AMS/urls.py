from django.contrib import admin
from django.urls import path
from AMSapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('renderlogin/', views.renderLogin),
    path('home/', views.renderHome),
    path('leave/', views.renderLeave),
    path('users/', views.renderUsers),
    path('time/', views.renderTimings),
    path('dologin/', views.doLogin),
    path('logout/', views.doLogout),
    path('clkin/', views.clockIn),
    path('clkout/', views.clockOut),
    path('brkin/', views.brkIn),
    path('brkout/', views.brkOut),
    path('apply/', views.doRequest),
    path('request/', views.renderRequest),
    path('status/', views.status),
    path('export/', views.export),
    path('add/', views.add),
    path('delete/', views.delete),
]
