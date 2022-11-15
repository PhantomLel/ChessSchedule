# Chess Tournement Manager
This app is designed to provide a kahoot-like experience to simplify managing chess tournements
# App structure
```
run // executable to run program
chessschedule
|- static // javascript, css.
    |- index.js
    |- components // a component is a distinct part of the page which we can break down into seperate files
        |- whatevercomponents.js // the javascript for a component
|- templates
    |- index.html // entry point from which all other components are either hidden or shown
    |- components
        |- whatevercomponent.html // the html for a component
|- models // models are classes that represent some data that we need to manipulate
    |- player.py 
    |- whatevermodel.py
|- routes // may or may not be necessary
    |- whateverroute.py
|- __main__.py // entry point

```