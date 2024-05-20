"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.signup("tes1", "test1@test.com", "password", None)
        user2 = User.signup("tes2", "test2@test.com", "password", None)

        user1.id = 111
        user2.id = 222

        db.session.commit()

        self.user1 = user1
        self.user2 = user2

        self.client = app.test_client()


    def tearDown(self):
        db.session.rollback()
        return super().tearDown()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_user_repr(self):
        """Test User _repr_ method works"""
        self.assertEqual(f"{self.user1}", f"<User #{self.user1.id}: {self.user1.username}, {self.user1.email}>")

    def test_user_follows(self):

        self.assertFalse(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_followed_by(self.user1))
        self.user1.following.append(self.user2)
        
        db.session.commit()

        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user2.followers), 1)
        self.assertEqual(len(self.user2.following), 0)

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertTrue(self.user2.is_followed_by(self.user1))


####################################################
    # User Create Test

    def test_user_create(self):

        test_user = User.signup(
            email="test@test.com",
            username="test_user",
            password="HASHED_PASSWORD",
            image_url=None
        )
        tid = 100
        test_user.id = tid

        db.session.commit()
        
        test_user = User.query.get(tid)
        self.assertIsNotNone(test_user)
        self.assertEqual(test_user.username, "test_user")
        self.assertEqual(test_user.email, "test@test.com")
        self.assertEqual(test_user.id, 100)
        self.assertNotEqual(test_user.password, "HASHED_PASSWORD")
        self.assertTrue(test_user.password.startswith("$2b$"))

    def test_wrong_username(self):      

        failed = User.signup(None, "test4@test.com", "password", None)
        failed.id = 2000

        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_wrong_password(self):       

        with self.assertRaises(ValueError):
            User.signup("test3", "test4@test.com", None, None)

    def test_wrong_email(self):  
        
        failed = User.signup("test3", None, "password", None)
        failed.id = 2000
    
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()


####################################################
    # User Authentication Test
            
    def test_user_authentication(self):

        user = User.authenticate(username=self.user1.username, password="password")
        self.assertIsNot(user, False)
        self.assertEqual(user, self.user1)

    def test_wrong_user_authentication(self):
        """
        Testing wrong authentication of the user
        Wrong password or username will return false
        """

        user1 = User.authenticate(username=self.user1.username, password="pkdsasd")
        user2 = User.authenticate(username="test", password=self.user1.password)

        self.assertFalse(user1)
        self.assertFalse(user2)

    


    



