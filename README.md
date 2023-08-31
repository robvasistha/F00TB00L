# F00TB00L - CS50 Final project
#### Video Demo:  <https://www.youtube.com/watch?v=kO-CfcXz7tI>
#### Description:
F00TB00L is a Full Stack Flask Web Application which allows users to log into a dashboard to see their teams upcoming fixtures, import fixtures into their calendar, squad information, and league standings.

The main motivation behind F00TB00L came from me wanting to be aware of when my teams upcoming matches were without the need to manually search for when they will be as I am not always free to do so.
I wanted to have a platform where I can see all of my teams upcoming games, information and league standings all in one place so that I don't have to look elsewhere, thereby solving my problem.

This project uses inspiration from CS50's Week 9 assignment: Finance, and is also a Flask Web application that uses Python and SQL for backend and HTML, CSS and JS for frontend.

#### Minimum Viable Product:
##### Registration ✅
* User should be able to select username, password, and their team.
* User can type their teamname to refine number of results to get their team.
* When the user is registered they are assigned a unique ID in the database, stored with their username, hashed password, and team_id.

##### Login ✅
* User should be able to log in with their registered information.
* User should not be able to enter application with invalid login.

##### Dashboard ✅
* Navigation bar at the top for switching pages between dashboard, squad and table.
* Dashboard greets user by referencing their username from database, as well as displaying their teams icon.
* Calendar with all of the upcoming fixtures for the users team as events in the Calendar.
* Button which enables the user to download the calendar into a .ics file which can be imported into digital calendar of choice.

##### Table ✅
* Show Current standings of the league table of the users club

##### Squad ✅
* List all of the user's teams players as well as some information about them like Nationality, Position and Date of Birth

#### Future development:
I have managed to finish my MVP and so I am satisfied to submit this as my final project.
If I were to continue development of this project I would perhaps include:
* Include Google OAuth so that the user can get their fixtures to their calendar in one click.
* User blog where people can post and discuss recent events with people who share the same club
* Individual match statistics like head-to-head history and match win prediction
* Allow the user to select multiple teams
* Change the theme of the application based on the club's colour's
