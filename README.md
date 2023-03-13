# Kanban Board

Demo link: 


# Project Structure 

`/static` css files and js.

`/templates/auth` html files for authorization pages (register, login)

`/templates/blog` html files for kanban page

`/app.py` initializes project

`/tests` test files. Tests for: kanban operations (add, move, delete).


# Run Application

### macOS:

`python3 -m venv venv`
`source venv/bin/activate`
`pip3 install -r requirements.txt`
`python3 app.py`

### Windows:

`python3 -m venv venv`
`venv\Scripts\activate.bat`
`pip3 install -r requirements.txt`
`python3 app.py`


# Unit Tests

`python3 -m unittest discover`


# References

The code was adapted from the following resource:

Flask Tutorial. (n.d.). Retrieved October 10, 2022.
> https://flask.palletsprojects.com/en/2.2.x/tutorial/
