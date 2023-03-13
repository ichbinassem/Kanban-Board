from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect, session
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from auth import login_required
from db import get_db

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    """
    Display posts according to Kanban categories for current user

    Parameters
    -----------
    None

    Returns
    -----------
    Index page of Kanban with tasks classified into To Do, Doing, and Done categories


    """
    db = get_db()

    try:
        #keeping current user's id to select their own posts
        _id = session["user_id"]
        

        posts = db.execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " ORDER BY created DESC"
        ).fetchall()

        #most recent post goes first
        posts_todo = db.execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            f" WHERE p.status = 0 AND p.author_id = {_id}"
            " ORDER BY created DESC"
        ).fetchall()

        posts_doing = db.execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            f" WHERE p.status = 1 AND p.author_id = {_id}"
            " ORDER BY created DESC"
        ).fetchall()

        posts_done = db.execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            f" WHERE p.status = 2 AND p.author_id = {_id}"
            " ORDER BY created DESC"
        ).fetchall()
        return render_template("blog/index.html", posts=posts, posts_todo=posts_todo, posts_doing=posts_doing, posts_done=posts_done)
    except:
        return redirect(url_for("auth.register"))

    


def get_post(id, check_author=True):
    """
    Get a posts for a current user.
    Posts are quieried accordingly from cetgories in index page.

    Parameters
    -----------
    - id: post id
    - check_author: id of the post's author

    Returns
    -----------
    post with given id

    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )
    #raise errors when no post or incorrect author
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post



@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """
    Creating new posts for the current user

    Parameters
    -----------
    None

    Returns
    -----------
    Index Kanban page with all previous and added post

    """
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        status = 0
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)

        #insering new post into database
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, status, author_id) VALUES (?, ?, ?, ?)",
                (title, body, status, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """
    Updating posts in the current session

    Parameters
    -----------
    id: post's unique id

    Returns
    -----------
    Index Kanban page with an updated post

    """
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        
        #updating post details in database
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)

@bp.route("/<int:id>/move_doing", methods=("POST",))
@login_required
def move_doing(id):
    """
    Update post's status to "doing"

    Parameters
    -----------
    id: post's unique id

    Returns
    -----------
    Index Kanban page with a post moved to Doing category

    """
    post = get_post(id)
    status = 1
    error = None

    if error is not None:
        flash(error)
    
    #update status in the database
    else:
        db = get_db()
        db.execute(
            "UPDATE post SET status = ? WHERE id = ?", (status, id)
        )
        db.commit()
        return redirect(url_for("blog.index"))

    return render_template("blog/index.html", post=post)


@bp.route("/<int:id>/move_done", methods=("POST",))
@login_required
def move_done(id):
    """
    Update post's status to "done"

    Parameters
    -----------
    id: post's unique id

    Returns
    -----------
    Index Kanban page with a post moved to Done category

    """
    post = get_post(id)
    status = 2
    error = None

    if error is not None:
        flash(error)

    #update status in the database
    else:
        db = get_db()
        db.execute(
            "UPDATE post SET status = ? WHERE id = ?", (status, id)
        )
        db.commit()
        return redirect(url_for("blog.index"))

    return render_template("blog/index.html", post=post)

@bp.route("/<int:id>/move_todo", methods=("POST",))
@login_required
def move_todo(id):
    """
    Update post's status to "to do"

    Parameters
    -----------
    id: post's unique id

    Returns
    -----------
    Index Kanban page with a post moved to To Do category

    """
    post = get_post(id)
    status = 0
    error = None

    if error is not None:
        flash(error)
    
    #updates status in the database
    else:
        db = get_db()
        db.execute(
            "UPDATE post SET status = ? WHERE id = ?", (status, id)
        )
        db.commit()
        return redirect(url_for("blog.index"))

    return render_template("blog/index.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """
    Delete a post.

    Parameters
    -----------
    id: post's unique id

    Returns
    -----------
    Index Kanban page without deleted post

    """
    get_post(id)
    db = get_db()

    #deletes post from database
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
