import functools

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """
    When user is not logged in, redirects to login page

    Parameters
    ------------
    view: base html template

    Returns
    ------------
    wrapped Login page

    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """
    When user's session is continued, current user's data is accessible by g.user
    Keeps current user's credentials

    Parameters
    -----------
    None

    Returns
    -----------
    None

    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = (
            get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
        )


@bp.route("/register", methods=("GET", "POST"))
def register():
    """
    Registers a new user

    Parameters
    -----------
    None

    Returns
    -----------
    When successfully registered, redirects to Log In page

    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        #username is unique
        if error is None:
            try:
                #hashing the password
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            
            #validate username is unique
            except db.IntegrityError:
                error = f"User {username} is already registered."
            
            #redurect to log in, when successfully registered
            else:
                flash("Succesfully registered. Login with your credentials.")
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """
    Log in registered users

    Parameters
    -----------
    None

    Returns
    -----------
    - When successfully logged in redirects to Index page with Kanban
    - When username is not found redirects to Register page

    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        try:
            user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
            ).fetchone()
        except:
            flash("You need to create an account first")
            return redirect(url_for("auth.register"))

        #check credentials
        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        #create new session for logged in user
        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))


        flash(error)

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """
    Clear the current session
    Logs user out

    Parameters
    -----------
    None

    Returns
    -----------
    Redirects to Login page

    """
    session.clear()
    return redirect(url_for("auth.login"))
