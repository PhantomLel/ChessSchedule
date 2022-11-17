# Chess Tournament Manager
This app is designed to provide a kahoot-like experience to simplify managing chess tournaments
Users connect to the web-app and provide basic information about themselves (name, experience-level, ect.) and the web apps makes pairings of players to play against each other. These pairings get better over time, as the system uses an elo system to make match-ups.
# App structure
```
run // executable to run program
chessschedule
|- static // javascript, css.
    |- index.js
    |- main.css
    |- components // a component is a distinct part of the page which we can break down into seperate files
        |- whatevercomponents.js // the javascript for a component
|- templates
    |- index.html // entry point from which all other components are either hidden or shown
    |- components
        |- whatevercomponent.html // the html for a component
|- models // models are classes that represent some data that we need to manipulate
    |- player.py 
    |- whatevermodel.py
|- algos // anything independant of the actual web server
    |- algo.py
|- routes // may or may not be necessary
    |- flask_routes.py 
    |- socketio_routes.py
|- __main__.py // entry point
|- app.py // app init

```
