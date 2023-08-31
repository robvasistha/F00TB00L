import os
import requests
import json
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_file
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from icalendar import Calendar, Event, vCalAddress, vText
from datetime import datetime, timedelta
from dateutil import parser
from pathlib import Path
import pytz

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Configure session to use filesystem instead of cookies.
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///footbool.db")

# Make sure API key is set
headers = {
        'X-Auth-Token': '1964b441b0df4396bb65ea0bf824ad12'
    }

# initialise calendar
cal = Calendar()
# Some properties are required to be compliant
cal.add('prodid', 'F00TB00L calendar')
cal.add('version', '2.0')

@app.route('/download_fixtures')
def download_fixtures():
    p = "fixtures.ics"
    return send_file(p, as_attachment=True)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
@login_required
def index():
    """Show homepage"""
    uri = 'https://api.football-data.org/v4/teams?limit=500'
    response = requests.get(uri, headers=headers)
    teams_json= response.json()
    username = db.execute("SELECT username FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["username"]
    teamid = db.execute("SELECT teamid FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["teamid"]
    for x in range(len(teams_json['teams'])):
        if teams_json['teams'][x].get('id') == teamid:
            teamCrest = teams_json['teams'][x].get('crest')
    matches_uri = "https://api.football-data.org/v4/teams/" + str(teamid) + "/matches"
    matchesResponse = requests.get(matches_uri, headers=headers)
    matches_json = matchesResponse.json()
    matchesList=[]
    for y in range(len(matches_json['matches'])):
        match = {
                 "id" : matches_json['matches'][y].get('id'),
                 "title" : matches_json['matches'][y]['homeTeam'].get('shortName') + " vs. " + matches_json['matches'][y]['awayTeam'].get('shortName'),
                 "start"  : matches_json['matches'][y]['utcDate']}
        matchesList.append(match)

    for m in range(len(matchesList)):
        ds = matchesList[m]['start']
        date = parser.parse(ds)
        event = Event()
        event.add('summary', matchesList[m]['title'])

        event.add('dtstart', date)
        event.add('dtend', date + timedelta(hours=1))
        cal.add_component(event)
    # Write to disk
    directory = Path.cwd()
    try:
        directory.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("Folder already exists")
    else:
        print("Folder was created")

    f = open(os.path.join(directory, 'fixtures.ics'), 'wb')
    f.write(cal.to_ical())
    f.close()

    return render_template("index.html", username=username, teamCrest=teamCrest,
                               matchesList=matchesList)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    if os.path.exists("fixtures.ics"):
        os.remove("fixtures.ics")
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # clear any previous user id
    if os.path.exists("fixtures.ics"):
        os.remove("fixtures.ics")
    session.clear()
    uri = 'https://api.football-data.org/v4/teams?limit=500'
    response = requests.get(uri, headers=headers)
    teams_json= response.json()
    teams_list=[]
    for team in range(len(teams_json['teams'])):
        teams_list.append(teams_json['teams'][team].get('name'))#] = teams_json['teams'][team].get(id)

    uri = 'https://api.football-data.org/v4/teams?limit=500'
    response = requests.get(uri, headers=headers)
    teams_json= response.json()
    # check user submitted via POST
    if request.method == "POST":
        # check user submits username
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # check user submits password
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        # check user confirmed password
        elif not request.form.get("confirmation", 400):
            return apology("must re-enter password", 400)
        # check passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)
        # check for username in db with SQL query.
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # check username doesnt already exist in the db
        if len(rows) != 0:
            return apology("username already exists", 400)
        # add new use to the db with SQl query
        teampick = request.form.get("team")
        for pick in range(len(teams_json['teams'])):
            if teams_json['teams'][pick].get('name') == teampick:
                id = teams_json['teams'][pick].get('id')
        db.execute("INSERT INTO users (username, hash, teamid) VALUES (?, ?, ?)",
                   request.form.get("username"), generate_password_hash(request.form.get("password")), id)
        # check db for new user with SQl
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # provide session with the user id.
        session["user_id"] = rows[0]["id"]
        # redirect user to homepage
        return redirect("/")
    # if the user reached route by GET
    else:
        return render_template("register.html", teams_list=teams_list)

@app.route("/table")
@login_required
def table():
    # get all comps into a list
    comps_uri = "https://api.football-data.org/v4/competitions"
    compsResponse = requests.get(comps_uri, headers=headers)
    comps_json = compsResponse.json()
    compsList=[]

    for m in range(len(comps_json['competitions'])):
        comp = comps_json['competitions'][m].get('code')
        compsList.append(comp)

    # get user's team's id to get all their supported, running, non-cup competitions so that a table can be extracted from API
    teamid = db.execute("SELECT teamid FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["teamid"]
    teamcomps_uri = "https://api.football-data.org/v4/teams/" + str(teamid)
    teamcompsResponse = requests.get(teamcomps_uri, headers=headers)
    teamcomps_json = teamcompsResponse.json()
    teamcompsList=[]

    for i in range(len(teamcomps_json['runningCompetitions'])):
        if teamcomps_json['runningCompetitions'][i].get('type') != "CUP":
            teamcomp = teamcomps_json['runningCompetitions'][i].get('code')
            teamcompsList.append(teamcomp)
    # sort competitions into a common list between the teams competitions and the competitions supported to avoid errors.
    # this is because some of their running competitions are unsupported by the free tier of the API
    commonList=[]
    teamcompsList.sort()
    compsList.sort()
    for x in range(len(teamcompsList)):
        for y in range(len(compsList)):
            if (teamcompsList[x] == compsList[y]):
                commonList.append(teamcompsList[x])
    #count variable to increment for the length of the comps common
    count = 0
    commonListLen = len(commonList)
    compStandingsList =[]
    while count < commonListLen:
        #get the standings for each competition in that list
        standings_uri = "https://api.football-data.org/v4/competitions/" + commonList[count] +"/standings" #BL1
        standingsResponse = requests.get(standings_uri, headers=headers)
        standings_json = standingsResponse.json()
        #create standing list then iterate through standings json to get the data for the standings table, inside loop to clear list
        standingsList=[]
        for i in range(len(standings_json['standings'])):
            for j in range(len(standings_json['standings'][i]['table'])):
                standings = {
                    "position" : standings_json['standings'][i]['table'][j].get('position'),
                    "name" : standings_json['standings'][i]['table'][j]['team'].get('name'),
                    "gp" : standings_json['standings'][i]['table'][j].get('playedGames'),
                    "w" : standings_json['standings'][i]['table'][j].get('won'),
                    "d" : standings_json['standings'][i]['table'][j].get('draw'),
                    "l" : standings_json['standings'][i]['table'][j].get('lost'),
                    "gd" : standings_json['standings'][i]['table'][j].get('goalDifference'),
                    "points" : standings_json['standings'][i]['table'][j].get('points')
                }
                #append standings dict to the standings list
                standingsList.append(standings)
        #append standings list to the compstandinglist which is a list of lists
        compStandingsList.append(standingsList)
        #increment counter
        count +=1

    return render_template("table.html", compStandingsList=compStandingsList, commonList=commonList,standingsList=standingsList)

@app.route("/squad")
@login_required
def squad():
    teamid = db.execute("SELECT teamid FROM users WHERE id = :user_id", user_id=session["user_id"])[0]["teamid"]
    uri = 'https://api.football-data.org/v4/teams/' + str(teamid)
    response = requests.get(uri, headers=headers)
    squad_json= response.json()

    squad_list=[]
    for player in range(len(squad_json['squad'])):
        member = {
            "name": squad_json['squad'][player].get('name'),
            "position": squad_json['squad'][player].get('position'),
            "nationality": squad_json['squad'][player].get('nationality'),
            "dob": squad_json['squad'][player].get('dateOfBirth'),
        }
        squad_list.append(member)
    return render_template("squad.html", squad_list = squad_list)
