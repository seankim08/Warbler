"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()

        user1 = User.signup("tes1", "test1@test.com", "password", None)
        user2 = User.signup("tes2", "test2@test.com", "password", None)

        user1.id = 111
        user2.id = 222

        db.session.commit()

        self.user1 = user1
        self.user2 = user2
        
        self.client = app.test_client()
        
    def test_user_profile(self):
        """Can use see the user profile?"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                
            resp = c.get(f"/users/{self.user1.id}")
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.user1.username, str([resp.data]))
        
    def test_invalid_user_profile(self):
        """Can use see not-existing user profile?"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
                
            resp = c.get(f"/users/9999")
            
            self.assertEqual(resp.status_code, 404)
    
    def test_show_followers(self):
        """Can use see the followers?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        
        self.user2.following.append(self.user1)
            
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            resp = c.get(f"/users/{self.user1.id}/followers")
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.user1.username, str([resp.data]))
            
    def test_show_following(self):
        """Can use see the following users?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        
        self.user1.following.append(self.user2)
            
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            resp = c.get(f"/users/{self.user1.id}/following")
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.user1.username, str([resp.data]))
            
    def test_authentication_show_followers(self):
        """Can use see the followers without authentication?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        
        self.user2.following.append(self.user1)
            
        db.session.commit()

        with self.client as c:
            
            resp = c.get(f"/users/{self.user1.id}/followers", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            
    def test_authentication_show_following(self):
        """Can use see the following users without authentication?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        
        self.user1.following.append(self.user2)
            
        db.session.commit()

        with self.client as c:
            
            resp = c.get(f"/users/{self.user1.id}/followers", follow_redirects=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
    
    def test_toggle_like(self):
        """Can use toggle a like of the message?"""
        
        msg = Message(text = "testing", 
                          user_id = self.user2.id,
                          id = 111)
        
        db.session.add(msg)
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
        
            # add a like of the message
            resp = c.post("/users/toggle_like/111",  follow_redirects=True)
            likes = Likes.query.filter(Likes.message_id == 111).all()
        
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.user1.id)
        
            # remove a like of the message
            resp = c.post("/users/toggle_like/111",  follow_redirects=True)
        
            likes = Likes.query.filter(Likes.message_id == 111).all()
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(likes), 0)
        
    def test_unauthorized_toggle_like(self):
        """Can use toggle a like of the message without authorization?"""
        
        msg = Message(text = "testing", 
                          user_id = self.user2.id,
                          id = 111)
        
        db.session.add(msg)
        db.session.commit()
        
        with self.client as c:
            
            resp = c.post("/users/toggle_like/111",  follow_redirects=True)
            
            likes = Likes.query.filter(Likes.message_id == 111).all()
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(len(likes), 0)
  
    