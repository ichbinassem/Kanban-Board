import os

from flask import Flask


def create_app(test_config=None):
    """
    Creating an instance of an Kanban Board

    Parameters
    -----------
    None

    Returns
    -----------
    Functional Kanban Board using all templates
    
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # Signs sessions cookies for each config
        SECRET_KEY="dev",
        # stores database
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # loding the indtance config
        app.config.from_pyfile("config.py", silent=True)
    else:
        # testing config
        app.config.update(test_config)

    # checking path to database folder
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # setting up database commands
    import db

    db.init_app(app)

    # setting up blueprints
    import auth, blog

    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)
    
    with app.app_context():
        db.init_db()

    #setting main page
    app.add_url_rule("/", endpoint="index")

    return app

create_app()