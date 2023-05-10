# -*- coding: utf-8 -*-
# @Author: Eduardo Santos
# @Date:   2023-04-11 16:20:38
# @Last Modified by:   Eduardo Santos
# @Last Modified time: 2023-04-11 17:38:22

from django.http import HttpRequest
from django.shortcuts import render, redirect
from f1_app.queries import races_queries
from f1_app.queries import standings_queries
from f1_app.queries import teams_queries
from f1_app.queries import drivers_queries
from f1_app.queries import curiosities as curiosities_queries
from f1_app.queries import admin_queries
from app.forms import *
from django.contrib.auth import update_session_auth_hash

# Create your views here.
def start(request):
    return render(request, 'index.html')


def register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            return redirect('home')
        else:
            return render(request, 'signup.html', {'form': form})
    else:
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})


cities = {
    "Australian Grand Prix" : "Melbourne, Australia",
    "Bahrain Grand Prix" : "Sakhir, Bahrain",
    "Chinese Grand Prix" : "Shanghai, China",
    "Azerbaijan Grand Prix" : "Baku, Azerbaijan",
    "Spanish Grand Prix" : "Montmeló, Spain",
    "Monaco Grand Prix" : "Monaco, France",
    "Canadian Grand Prix" : "Montreal, Canada",
    "French Grand Prix" : "Le Castellet, France",
    "Austrian Grand Prix" : "Spielberg, Austria",
    "British Grand Prix" : "Silverstone, UK",
    "German Grand Prix" : "Nürburg, Germany",
    "Hungarian Grand Prix" : "Budapest, Hungaria",
    "Belgian Grand Prix" : "Ardennes, Belgium",
    "Italian Grand Prix" : "Milan, Italy",
    "Singapore Grand Prix" : "Marina Bay, Singapore",
    "Russian Grand Prix" : "Sochi Autodrom, Russia",
    "Japanese Grand Prix" : "Shizuoka, Japan",
    "Mexican Grand Prix" : "Mexico City, Mexico",
    "United States Grand Prix" : "Austin, Texas, USA",
    "Brazilian Grand Prix" : "São Paulo, Brazil",
    "Abu Dhabi Grand Prix" : "Yas Island, UAE",
    "Styrian Grand Prix" : "Styria, Austria",
    "70th Anniversary Grand Prix" : "Silverstone, UK",
    "Tuscan Grand Prix" : "Tuscany, Italy",
    "Eifel Grand Prix" : "Nürburg, Germany",
    "Portuguese Grand Prix" : "Portimão, Portugal",
    "Emilia Romagna Grand Prix" : "Emilia Romagna, Italy",
    "Turkish Grand Prix" : "Istambul, Turkey",
    "Sakhir Grand Prix" : "Sakhir, Bahrain",
    "Dutch Grand Prix" : "Amsterdam, Netherlands",
    "Mexico City Grand Prix" : "Mexico City, Mexico",
    "São Paulo Grand Prix" : "São Paulo, Brazil",
    "Qatar Grand Prix" : "Doha, Qatar",
    "Saudi Arabian Grand Prix" : "Jeddah, Saudi Arabia",
    "Miami Grand Prix" : "Florida, USA"
}

def results(request, season):
    if request.user.is_authenticated:
        results = standings_queries.pilots_season_final_standings(season)
        if len(results):
            data = {'data': results}
            #print(data)
        else:
            data = {'error': True}
            print("error")
        return render(request, "results.html", data)
    else:
        return redirect('home')

def teams(request):
    if request.user.is_authenticated:
        teams = teams_queries.get_all_teams()
        final_teams = []
        teams_history = {}
        for team in teams:
            championships = standings_queries.team_total_championships(team[0])
            teams_history[team[0]] = sorted(teams_queries.get_team_drivers(team[0]), key=lambda x: x[0], reverse=True)
            if championships:
                final_teams.append((team[0], team[1], championships[2]))
            else:
                final_teams.append((team[0], team[1], '0'))
        
        sorted_list = sorted(final_teams, key=lambda x: x[2], reverse=True)

        data = {'data': sorted_list, 'teams_history': teams_history}
        #print(data)
        return render(request, "teams.html", data)
    else:
        return redirect('home')

def drivers(request):
    if request.user.is_authenticated:
        if 'driver_name' in request.GET and request.GET['driver_name']:
            driver_name = request.GET['driver_name']
            driver_info = drivers_queries.get_pilot_info(driver_name)

            drivers_history = {}

            if driver_info:
                championships = standings_queries.pilot_total_championships(driver_info[0])
                drivers_history[driver_info[0]] = sorted(drivers_queries.get_pilot_teams(driver_info[0]), key=lambda x: x[1], reverse=True)
                if championships:
                    driver_info = [(driver_info[0], driver_info[1], driver_info[2], driver_info[3], championships[4])]
                else:
                    driver_info = [(driver_info[0], driver_info[1], driver_info[2], driver_info[3], '0')]
                
                return render(request, "drivers.html", {'data': driver_info, 'drivers_history': drivers_history})
            else:
                return render(request, "drivers.html", {'data': []})
            
        else:
            drivers = drivers_queries.list_all_pilots()
            
            final_drivers = []
            drivers_history = {}
            for driver in drivers:
                championships = standings_queries.pilot_total_championships(driver[0])
                drivers_history[driver[0]] = sorted(drivers_queries.get_pilot_teams(driver[0]), key=lambda x: x[1], reverse=True)
                if championships:
                    final_drivers.append((driver[0], driver[1],  driver[2],  driver[3], championships[4]))
                else:
                    final_drivers.append((driver[0], driver[1],  driver[2],  driver[3], '0'))
            
            sorted_list = sorted(final_drivers, key=lambda x: x[4], reverse=True)

            data = {'data': sorted_list, 'drivers_history': drivers_history}

            return render(request, "drivers.html", data)
    else:
        return redirect('home')
    
def races(request, season):
    if request.user.is_authenticated:
        races = races_queries.races_by_season(season)
        new_races = []
        for race in races:
            new_races.append((race[0], race[1], cities[race[1]], race[3], season))

        #print(new_races)
        if len(new_races):
            data = {'data': new_races}
        else:
            data = {'error': True}
            print("error")
        return render(request, "races.html", data)
    else:
        return redirect('home')
    

def race_info(request, season, race_name):
    if request.user.is_authenticated:
        race_info = races_queries.all_pilots_standings_by_race_by_season(race_name, season)
        #print(race_info)
        if len(race_info):
            data = {'data': race_info}
        else:
            data = {'error': True}
        return render(request, "race-modal.html", data)
    else:
        return redirect('home')
    

def curiosities(request, season):
    top3 = curiosities_queries.pilots_finished_top3_by_season(season)[0:6]
    top_retired = curiosities_queries.pilots_most_retired_cars_by_season(season)[0:6]
    to3_accidents = curiosities_queries.pilots_most_accidents_by_season(season)[0:6]

    experienced_pilots = curiosities_queries.experience_drivers()
    best_pilots = curiosities_queries.best_pilots()[0:6]
    best_teams = curiosities_queries.best_teams()[0:6]

    all_pilots = drivers_queries.list_all_pilots()
    nationalities = [pilot[3] for pilot in all_pilots]


    data = {'top_3': top3, 'top_retired': top_retired, 'top_accidents': to3_accidents, 
            'experienced_pilots': experienced_pilots, 'best_pilots': best_pilots, 'best_teams': best_teams, 'nats': nationalities}

    return render(request, 'curiosities.html', data)



###### ADMIN ######

def admin_crud(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return render(request, 'admin.html')
        else:
            return redirect('notfound')
    else:
        return redirect('/login')
    
def add_driver(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            data = {}
            if request.method == "POST":
                form = CreateDriverForm(request.POST)

                if form.is_valid():    
                    response = admin_queries.create_pilot(form.cleaned_data['forename'], form.cleaned_data['surname'], form.cleaned_data['nationality'], form.cleaned_data['code'])

                    if response['status_code'] == 204:
                        data['success'] = 'Successfully added a new driver!'
                        form = CreateDriverForm()
                        return render(request, 'add-driver.html', {'data' : data, 'form': form})
                    
                    else:
                        data['error'] = 'Error creating the driver, make sure you are correctly filling the fields.'
                        form = CreateDriverForm()
                        return render(request, 'add-driver.html', {'data' : data, 'form': form})
                    
            else:
                form = CreateDriverForm()
                return render(request, 'add-driver.html', {'form': form})
        else:
            return redirect('notfound')
    else:
        return redirect('/login')
    
def add_team(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            data = {}
            if request.method == "POST":
                form = CreateTeamForm(request.POST)

                if form.is_valid():    
                    response = admin_queries.create_team(form.cleaned_data['name'], form.cleaned_data['nationality'])

                    if response['status_code'] == 204:
                        data['success'] = 'Successfully added a new team!'
                        form = CreateTeamForm()
                        return render(request, 'add-team.html', {'data' : data, 'form': form})
                    
                    else:
                        data['error'] = 'Error creating the team, make sure you are correctly filling the fields.'
                        form = CreateTeamForm()
                        return render(request, 'add-team.html', {'data' : data, 'form': form})
                    
            else:
                form = CreateTeamForm()
                return render(request, 'add-team.html', {'form': form})
        else:
            return redirect('notfound')
    else:
        return redirect('/login')

def delete_driver(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            data = {}
            if request.method == "POST":
                form = DeleteDriverForm(request.POST)

                if form.is_valid():    
                    response = admin_queries.delete_pilot(form.cleaned_data['code'])

                    if response['status_code'] == 204:
                        data['success'] = 'Successfully deleted the driver!'
                        form = DeleteDriverForm()
                        return render(request, 'delete-driver.html', {'data' : data, 'form': form})
                    
                    else:
                        data['error'] = 'Error deleting the driver, make sure the driver\'s code is correct.'
                        form = DeleteDriverForm()
                        return render(request, 'delete-driver.html', {'data' : data, 'form': form})
                    
            else:
                form = DeleteDriverForm()
                return render(request, 'delete-driver.html', {'form': form})
        else:
            return redirect('notfound')
    else:
        return redirect('/login')
    
def delete_team(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            data = {}
            if request.method == "POST":
                form = DeleteTeamForm(request.POST)

                if form.is_valid():    
                    response = admin_queries.delete_team(form.cleaned_data['name'])

                    if response['status_code'] == 204:
                        data['success'] = 'Successfully deleted the team!'
                        form = DeleteTeamForm()
                        return render(request, 'delete-team.html', {'data' : data, 'form': form})
                    
                    else:
                        data['error'] = 'Error deleting the team, make sure that the team exists.'
                        form = DeleteTeamForm()
                        return render(request, 'delete-team.html', {'data' : data, 'form': form})
                    
            else:
                form = DeleteTeamForm()
                return render(request, 'delete-team.html', {'form': form})
        else:
            return redirect('notfound')
    else:
        return redirect('/login')
    

def not_found(request):
    return render(request, 'not-found.html')