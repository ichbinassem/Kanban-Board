import os
import unittest
import tempfile
from app import create_app
from db import get_db, init_db


class TestDatabase(unittest.TestCase):
    def setUp(self):
        """
        Setting up the app for testing 

        Parameters
        -----------
        None

        Returns
        -----------
        None

        """

        #creating temporary file
        self.db_fd, self.db_path = tempfile.mkstemp()

        #initializing the app
        self.app = create_app({"TESTING": True, "DATABASE": self.db_path})

        #creating database
        with self.app.app_context():
            # create tables
            init_db()

            #inserting test data
            with self.app.open_resource('data.sql') as f:
                get_db().executescript(f.read().decode('utf8'))

        self.client = self.app.test_client()


    def tearDown(self):
        """
        Closes and removes temporary database

        Parameters
        -----------
        None

        Returns
        -----------
        None
        
        """

        os.close(self.db_fd)
        os.unlink(self.db_path)


    def test_get_users(self):
        """
        Checks the number of users with database

        Parameters
        -----------
        None

        Returns
        -----------
        None       
        
        """
        with self.app.app_context():
            #query all users from database
            cur = get_db().cursor()
            cur.execute('SELECT * FROM user')
            rows = cur.fetchall()

            self.assertEqual(len(rows), 2)


    def test_add_user(self):
        """
        Checks if items are added to the database

        Parameters
        -----------
        None

        Returns
        -----------
        None               

        """
        with self.app.app_context():
            #adding new user to a database
            cur = get_db().cursor()
            cur.execute('INSERT INTO user (username, password) VALUES (?, ?)',
                        ('test2', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'))
            get_db().commit()

            cur.execute('SELECT * FROM user WHERE username = ?', ('test2',))
            row = cur.fetchone()

            # check if new user was inserted successfully
            self.assertEqual(row['username'], 'test2')
            self.assertEqual(row['password'], 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f')


    def test_login(self):
        """
        Checks if Login page successfully redirects to Index page

        Parameters
        -----------
        None

        Returns
        -----------
        None                       
        
        """
        response = self.client.post(
            "/auth/login",
            data={"username": "test", "password": "test"}
        )

        self.assertEqual(response.status_code, 302)


    def test_logout(self):
        """
        Checks user is successfully logged out and redirected to Login page

        Parameters
        -----------
        None

        Returns
        -----------
        None               

        """
        response = self.client.get("/auth/logout")

        self.assertEqual(response.status_code, 302)


    def test_register(self):
        """
        Checks if user is correctly registered and redirected to Login page

        Parameters
        -----------
        None

        Returns
        -----------
        None               
        
        """
        with self.app.test_client() as client:
            #checks if register page works correctly
            response = client.get("/auth/register")
            self.assertEqual(response.status_code, 200)

            #test data for logging
            data = {"username": "a", "password": "a"}
            response2 = client.post("/auth/register", data=data, follow_redirects=True)

            #check if page redirects when login is successful
            self.assertEqual(response2.status_code, 200)


    def test_create(self):
        """
        Checks if task is created correctly

        Parameters
        -----------
        None

        Returns
        -----------
        None               
        
        """
        #log test user in
        self.client.post("/auth/login", data={"username": "test", "password": "test"})

        #check if path exists
        response = self.client.get("/create")
        self.assertEqual(response.status_code, 200)

        #create test task and check if it redirects to Index page
        response = self.client.post("/create", data={"title": "test_create", "body": "test_create"})
        self.assertEqual(response.status_code, 302)

        #check if task matches in the database
        with self.app.app_context():
            db = get_db()
            post = db.execute("SELECT * FROM post ORDER BY id DESC").fetchone()
            self.assertEqual(post["title"], "test_create")
            self.assertEqual(post["body"], "test_create")


    def test_update(self):
        """
        Checks if task is updated successfully

        Parameters
        -----------
        None

        Returns
        -----------
        None               
        
        """
        self.client.post("/auth/login", data={"username": "test", "password": "test"})
        response = self.client.get("/1/update")
        self.assertEqual(response.status_code, 200)

        #update test task and check if it redirects to Index page
        response = self.client.post("/1/update", data={"title": "updated", "body": ""})
        self.assertEqual(response.status_code, 302)

        #check if database is updated
        with self.app.app_context():
            db = get_db()
            post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
            self.assertEqual(post["title"], "updated")


    def test_doing(self):
        """
        Checks if task is correctly moved to Doing category

        Parameters
        -----------
        None

        Returns
        -----------
        None               
        
        """
        self.client.post("/auth/login", data={"username": "test", "password": "test"})
        response = self.client.post("/1/move_doing")
        self.assertEqual(response.status_code, 302)

        #check if task status is updated to doing
        with self.app.app_context():
            db = get_db()
            post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
            self.assertEqual(post["status"], 1)


    def test_done(self):
        """
        Checks if task is correctly moved to Done category

        Parameters
        -----------
        None

        Returns
        -----------
        None               
        
        """
        self.client.post("/auth/login", data={"username": "test", "password": "test"})
        response = self.client.post("/1/move_done")
        self.assertEqual(response.status_code, 302)

        #check if task status is updated to done
        with self.app.app_context():
            db = get_db()
            post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
            self.assertEqual(post["status"], 2)


    def test_todo(self):
        """
        Checks if task is correctly moved to To Do category

        Parameters
        -----------
        None

        Returns
        -----------
        None               
        
        """
        self.client.post("/auth/login", data={"username": "test", "password": "test"})
        response = self.client.post("/1/move_todo")
        self.assertEqual(response.status_code, 302)

        #check if task status is updated to done
        with self.app.app_context():
            db = get_db()
            post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
            self.assertEqual(post["status"], 0)


    def test_delete(self):
        """
        Checks if task is deleted correctly

        Parameters
        -----------
        None

        Returns
        -----------
        None               
        
        """
        self.client.post("/auth/login", data={"username": "test", "password": "test"})
        response = self.client.post("/1/delete")
        self.assertEqual(response.status_code, 302)

        #check if task is deleted from database
        with self.app.app_context():
            db = get_db()
            post = db.execute("SELECT * FROM post WHERE id = 1").fetchone()
            self.assertEqual(post, None)


if __name__ == '__main__':
    unittest.main()
