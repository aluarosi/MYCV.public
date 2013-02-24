"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import User, Group

# Local imports
from models import CredentialsRequest
# Python imports
from datetime import datetime


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)


class CredentialsRequestStatesTest(TestCase):
    def setUp(self):
        from MYCV.credentials.settings import GUESTS_L1
        Group( name= GUESTS_L1).save()
        User( username="admin").save()
        self.set_credentialsrequest()

    def set_credentialsrequest(self, email="test@test.com"):
        cr = CredentialsRequest (   email= email,
                                    name="Test",
                                    surname="Thorough",
                                    text="Please send me credentials",
                                    datetime =  datetime.now(),
                                )
        cr.save()
        self.cr = cr

    def create_user(self, username):
        User( username=username).save()

    def check_password_ok(self, value):
        try:
            user = User.objects.get(username = self.cr.email)
        except  User.DoesNotExist:
            user = None
        self.assertEqual    (   user and user.has_usable_password() and user.password != u'',
                                value
                            ) 
    
    def assign_password(self, password="12345678"):
        self.cr.state_manager.assign_password(password)

    def do_accept(self):
        self.cr.state_manager.accept()
    def do_reject(self):
        self.cr.state_manager.reject()
    def do_reset(self):
        self.cr.state_manager.reset()
    def do_sent(self):
        self.cr.state_manager.sent()

    def check_is_pending(self):
        """Checks if state is pending"""
        # State
        self.assertEqual(self.cr.state, "PEN")
        # State helpers
        self.assertTrue(self.cr.is_pending())
        self.assertFalse(self.cr.is_accepted())
        self.assertFalse(self.cr.is_rejected())
        self.assertFalse(self.cr.is_sent())
        self.assertFalse(self.cr.is_error())
        # Allowed actions
        self.assertEqual(   set(self.cr.state_manager.allowed_actions()),
                            set(['accept','reject'])
                        )

    def check_is_accepted(self):
        """Checks if state is accepted""" 
        # State
        self.assertEqual(self.cr.state, "ACC")
        # State helpers
        self.assertFalse(self.cr.is_pending())
        self.assertTrue(self.cr.is_accepted())
        self.assertFalse(self.cr.is_rejected())
        self.assertFalse(self.cr.is_sent())
        self.assertFalse(self.cr.is_error())
        # Allowed actions
        self.assertEqual(   set(self.cr.state_manager.allowed_actions()),
                            set(['reset','sent'])
                        )
        # User is assigned
        self.check_user_is_assigned(True)

    def check_is_rejected(self):
        """Checks if state is rejected""" 
        # State
        self.assertEqual(self.cr.state, "REJ")
        # State helpers
        self.assertFalse(self.cr.is_pending())
        self.assertFalse(self.cr.is_accepted())
        self.assertTrue(self.cr.is_rejected())
        self.assertFalse(self.cr.is_sent())
        self.assertFalse(self.cr.is_error())
        # Allowed actions
        self.assertEqual(   set(self.cr.state_manager.allowed_actions()),
                            set(['reset',])
                        )

    def check_is_sent(self):
        """Checks if state is sent""" 
        # State
        self.assertEqual(self.cr.state, "SNT")
        # State helpers
        self.assertFalse(self.cr.is_pending())
        self.assertFalse(self.cr.is_accepted())
        self.assertFalse(self.cr.is_rejected())
        self.assertTrue(self.cr.is_sent())
        self.assertFalse(self.cr.is_error())
        # Allowed actions
        self.assertEqual(   set(self.cr.state_manager.allowed_actions()),
                            set([])
                        )

    def check_is_error(self):
        """Checks if state is error""" 
        # State
        self.assertEqual(self.cr.state, "ERR")
        # State helpers
        self.assertFalse(self.cr.is_pending())
        self.assertFalse(self.cr.is_accepted())
        self.assertFalse(self.cr.is_rejected())
        self.assertFalse(self.cr.is_sent())
        self.assertTrue(self.cr.is_error())

    def check_user_is_assigned(self, value):
        try:
            user = User.objects.get(username=self.cr.email)
            user_already_exists = True
        except Exception:
            user_already_exists = False
        self.assertEqual(user_already_exists, value) 
    
    def test_state_cycle_ok_1(self):
        """ State cycle: PND --|accept|--> ACC --|sent|--> SNT
        """ 
        self.check_is_pending()
        self.do_accept()
        self.check_is_accepted()
        self.check_password_ok(False)
        self.assign_password()
        self.check_password_ok(True)
        self.do_sent()
        self.check_is_sent()

    def test_state_cycle_ok_2(self):
        """ State cycle: PND --> ACC --> PND --> REJ --> PND --> ACC --> SNT
        """ 
        self.check_is_pending()
        self.do_accept()
        self.check_is_accepted()
        self.check_password_ok(False)
        self.do_reset()
        self.check_is_pending()
        self.do_reject()
        self.check_is_rejected()
        self.do_reset()
        self.check_is_pending()
        self.do_accept()
        self.check_is_accepted()
        self.check_password_ok(False)
        self.assign_password()
        self.check_password_ok(True)
        self.do_sent()
        self.check_is_sent()

    def test_state_cycle_ok_3(self):
        """ State cycle: PND --> ACC -->|passwd set|--> PND --> REJ --> PND --> ACC --> SNT
        """ 
        self.check_is_pending()
        self.do_accept()
        self.check_is_accepted()
        self.check_password_ok(False)
        self.assign_password()
        self.check_password_ok(True)
        self.do_reset()
        self.check_is_pending()
        self.do_reject()
        self.check_is_rejected()
        self.do_reset()
        self.check_is_pending()
        self.do_accept()
        self.check_is_accepted()
        self.check_password_ok(True)
        self.assign_password()
        self.check_password_ok(True)
        self.do_sent()
        self.check_is_sent()

    def test_state_cycle_error_1(self):
        """ State cycle: PND --> ERR
        """ 
        # Credentials Request for an already existing user
        self.create_user("olduser@test.com")
        self.set_credentialsrequest("olduser@test.com")
        self.check_is_pending()
        self.do_accept()
        self.check_is_error()
        self.do_accept()
        self.check_is_error()
        self.do_reject()
        self.check_is_error()

    def test_example(self):
        """ (1) Accept 
            (2) Generate Password
            (3) Sent
        """
        self.assertEqual(self.cr.state, "PEN") 
        self.assertTrue(self.cr.is_pending())
        # (1) Accept
        try:
            user = User.objects.get(username=self.cr.email)
            user_already_exists = True
        except Exception:
            user_already_exists = False
        self.assertEqual(user_already_exists, False) 

        self.cr.state_manager.accept()
        # (1.1) Check that user has been created
        self.assertTrue(User.objects.get(username=self.cr.email))
        # (1.2) Check that state is now ACC 
        self.assertEqual(self.cr.state, "ACC")
        self.assertTrue(self.cr.is_accepted())

        # Try to change to SNT without password
        user = User.objects.get(username=self.cr.email)
        self.cr.state_manager.sent() 
        self.assertEqual(self.cr.state, "ACC")
        self.assertTrue(self.cr.is_accepted())
        # Generate password
        self.cr.state_manager.assign_password("12345678")  
        self.cr.state_manager.sent() 
        self.assertEqual(self.cr.state, "SNT")
        self.assertFalse(self.cr.is_accepted())
        self.assertTrue(self.cr.is_sent())
        # Try to get to other states unsuccessfully
        self.cr.state_manager.reset() 
        self.assertEqual(self.cr.state, "SNT")
        self.assertFalse(self.cr.is_pending())
        self.assertTrue(self.cr.is_sent())
        
        
        
        
        
