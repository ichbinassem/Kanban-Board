# Kanban Board

Demo link: https://www.loom.com/share/688392dd810d46daa564f9938ca27f8e

Kanban App helps users to organize their tasks and order them according to "to do", "doing", "done" categories.
A Kanban board is a simple task management tool. Every task that you add can be in one of three states:

1. To do
2. Doing
3. Done

Kanban can be used to create new task, update, or delete it. Kanban board is personalizable. Every user has their own account, and can see only their own tasks. Users can register, log in and out. The application runs using Flask framework. 



# Project Structure 

`/static` css files and js.

`/templates/auth` html files for authorization pages (register, login)

`/templates/blog` html files for kanban page

`/app.py` initializes project

`/tests` test files. Tests for: kanban operations (add, move, delete).


# Run Application

### macOS:

```python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
python3 app.py
```

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
