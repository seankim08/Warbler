"""Message model tests."""

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        
        user1 = User.signup("tes1", "test1@test.com", "password", None)
        user1.id = 111
        db.session.commit()

        self.user1 = user1

        self.client = app.test_client()
        
    def tearDown(self):
        db.session.rollback()
        return super().tearDown()

    def test_message_model(self):
        """Does basic model work?"""

        msg = Message(
            text="testing",
            user_id=self.user1.id
        )

        db.session.add(msg)
        db.session.commit()
        
        msgs = Message.query.filter(Message.user_id == self.user1.id).all()
        self.assertEqual(len(msgs), 1)
        

    def test_like_message(self):
        
        msg1 = Message(
            text="testing",
            user_id=self.user1.id
        )
        
        msg2 = Message(
            text="testing",
            user_id=self.user1.id
        )
        
        user2 = User.signup("tes2", "test2@test.com", "password", None)
        user2.id = 222
        
        db.session.add_all([user2, msg1, msg2])
        db.session.commit()
        
        user2.likes.append(msg1)
        
        db.session.commit()
        
        likes = Likes.query.filter(Likes.user_id == user2.id).all()
        
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].message_id, msg1.id)
        self.assertEqual(likes[0].user_id, user2.id)
