# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-04-11 16:20:38
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-04-11 17:27:41

"""f1_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from app import views
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/django/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('signup/', views.register, name='signup'),
    path('', views.start, name='home'),
    path('teams', views.teams, name="teams"),
    path('results/<int:season>', views.results, name="results"),
    path('races/<int:season>', views.races, name="races"),
    path('races/<int:season>/<str:race_name>', views.race_info, name="race"),
    path('drivers', views.drivers, name="driver"),
    path('curiosities/<int:season>', views.curiosities, name="curiosities"),

    # admin
    path('admin/crud', views.admin_crud, name="adminCrud"),
    path('admin/addDriver', views.add_driver, name="addDriver"),
    path('admin/addTeam', views.add_team, name="addTeam"),
    path('admin/deleteDriver', views.delete_driver, name="deleteDriver"),
    path('admin/deleteTeam', views.delete_team, name="deleteTeam"),


    path('404', views.not_found, name="notfound")
]
