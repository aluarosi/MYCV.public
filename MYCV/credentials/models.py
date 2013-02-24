from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.db.utils import IntegrityError
# Local modules
from settings import GUESTS_L1
# Python modules
from datetime import datetime

class CredentialsRequest(models.Model):
    STATES = (  ('PEN',"Pending"),
                ('REJ',"Rejected"),
                ('ACC',"Accepted"),
                ('SNT',"Sent"),
                ('ERR',"Error"),
             )

    email = models.EmailField()
    name = models.CharField(max_length=40)
    surname = models.CharField(max_length=40)
    text = models.TextField()
    datetime = models.DateTimeField()
    email_sent_to_admins = models.BooleanField(default=False)
    state = models.CharField(max_length=3, choices=STATES, default='PEN')
    user = models.ForeignKey(User, blank=True, null=True)
    error = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return "[%s][%s] %s" % (self.datetime, self.email, self.text[:100]) 

    class Meta:
        verbose_name = "Credentials Request"
        ordering = ['datetime']

    def __init__(self, *args, **kwargs):
        super(CredentialsRequest, self).__init__(*args, **kwargs)
        self.state_manager = CredentialsRequestStateManager(self)

    def send_mail(self):
        """ Sends e-mail to admin with the request for credentials """
        try:
            send_mail(  subject = 'MYCV Credentials Request',
                    message = "%s" % self.text,
                    from_email = self.email,
                    recipient_list = (adm[1] for adm in settings.ADMINS) 
                    )
        except Exception as e:
            # email could not be sent
            return False
        else:
            # email was sent successfully
            self.email_sent_to_admins = True
            self.save()
            return True 

    def is_accepted(self):
        return self.state == "ACC"

    def is_rejected(self):
        return self.state == "REJ"

    def is_pending(self):
        return self.state == "PEN"

    def is_sent(self):
        return self.state == "SNT"

    def is_error(self):
        return self.state == "ERR"


class CredentialsRequestStateManager(object):
    
    def __init__(self, credentials_request):
        self.req = credentials_request
        self.states =  {    'PEN': self.PendingState(self, self.req),
                            'REJ': self.RejectedState(self, self.req),
                            'ACC': self.AcceptedState(self, self.req),
                            'SNT': self.SentState(self, self.req),
                            'ERR': self.ErrorState(self, self.req),
                        }
    
        # Set Initial State in manager querying state in model
        self.state = self.states[credentials_request.state]

    def allowed_actions(self):
        return self.state.allowed_actions()
        
    # --------------------------------
    # Methods to trigger state changes.
    #   They are delegated to inner state object.
    # --------------------------------
    def _change_state(self, next_state):
        old_state = self.req.state
        # Changes state object in manager
        self.state = self.states[next_state] 
        # Changes state in model 
        self.req.state = next_state
        self.req.save()
        # Make note with state change
        note = CredentialsNote  (   time_creation = datetime.now(), 
                                    text = "State Change: %s --> %s" % (old_state, next_state),
                                    user = User.objects.get(username="admin"), 
                                    credentials_request = self.req
                                )
        note.save()
    
    def _do(self, action):
        """ Tries to execute an action
            Returns next state
        """
        next_state = self.state.do(action)
        if next_state:
            self._change_state(next_state)

    # Public actions
    # TODO: try to DRY this with Metaprogramming?
    # All of them return dict with 'message' and 'next_state'
    def accept(self):
        return self._do('accept')
        
    def reject(self):
        return self._do('reject')

    def reset(self):
        return self._do('reset')

    def sent(self):
        return self._do('sent')

    def is_allowed_accept(self):
        return 'accept' in self.allowed_actions()
        
    def is_allowed_reject(self):
        return 'reject' in self.allowed_actions()

    def is_allowed_reset(self):
        return 'reset' in self.allowed_actions()

    def is_allowed_sent(self):
        return 'sent' in self.allowed_actions()

    # "Out of State" methods
    def is_password_generation_allowed(self):
        if self.req.state == "ACC" and self.req.user:
            return True
        else:
            return False

    def assign_password(self, raw_password):
        """Saves password into user"""
        if not self.is_password_generation_allowed():
            # User does not exist and cannot be given passwd
            return False   
        else:
            self.req.user.set_password(raw_password)
            self.req.user.save()
            return True

    # State inner classes
    class State(object):
        """ Common code for state classes """

        def __init__(self, manager, req):
            # Dict with methods to call
            self.actions =   {   'accept': None,
                                 'reject': None,
                                 'reset': None,
                                 'sent': None,
                             } 
            # Binds to credentials request instance
            self.req = req

        def do(self, action):
            """ Tries to execute an action
                It does not change state, that is manager's responsibility
                Returns only next state
            """
            try:
                # Do the action
                return self.actions[action]()
            except KeyError:
                # Action not supported
                return  None
            except TypeError:
                # State change not allowed
                return  None
    
        def allowed_actions(self):
            """ Returns a list of allowed actions for this state"""   
            return [i for i in self.actions if self.actions[i]]
    
    class PendingState(State):
        def __init__(self, manager, req):
            super(CredentialsRequestStateManager.PendingState, self).__init__(manager, req)
            self.actions['accept'] = self.accept
            self.actions['reject'] = self.reject

        def accept(self):
            user = self.req.user
            if user:
                # If user already exists, make sure it is activated...
                user.is_active = True 
                user.save() 
                return  "ACC"
            else:
                # ...otherwise creates user
                u = User(   email = self.req.email,
                            username = self.req.email,  
                            first_name = self.req.name,
                            last_name = self.req.surname,
                            date_joined = self.req.datetime,
                            )
                try:
                    u.save()
                except IntegrityError:
                    # A user with that username already exists
                    self.req.error = "Email %s already registered in users database" % self.req.email
                    self.req.save()
                    return "ERR"
                else:
                    self.req.user = u
                    # Join the group 
                    group = Group.objects.get(name=GUESTS_L1) 
                    u.groups.add(group)
                    u.save()
                    self.req.save()
                    return "ACC"
            
        def reject(self): 
            user = self.req.user
            if user:
                # If user exists, de-activate it
                user.is_active = False
                user.save() 
            return  "REJ"
        
    class RejectedState(State):
        def __init__(self, manager, req):
            super(CredentialsRequestStateManager.RejectedState, self).__init__(manager, req)
            self.actions['reset'] = self.reset

        def reset(self):
            user = self.req.user
            if user:
                # If user exists, de-activate it
                user.is_active = False
                user.save() 
            return  "PEN"
            
    class AcceptedState(State):
        def __init__(self, manager, req):
            super(CredentialsRequestStateManager.AcceptedState, self).__init__(manager, req)
            self.actions['reset'] = self.reset
            self.actions['sent'] = self.sent

        def reset(self):
            user = self.req.user
            if user:
                # If user exists, de-activate it
                user.is_active = False
                user.save() 
            return  "PEN"

        def sent(self):
            user = self.req.user
            #TODO: check has_usable_password()
            if user and user.has_usable_password() and user.password != u'':
                return "SNT"
            else:
                return None
            
    class SentState(State):
        pass

    class ErrorState(State):
        pass


class CredentialsNote(models.Model):
    time_creation = models.DateTimeField()
    text = models.TextField()
    user = models.ForeignKey(User, blank=False, null=False)
    credentials_request = models.ForeignKey(CredentialsRequest, blank=False, null=False)
    
    def __unicode__(self):
        return "NOTE for CR %s: [%s][%s] %s" % (self.credentials_request.id, self.user, self.time_creation, self.text[:100]) 

    class Meta:
        verbose_name = "Note"
        ordering = ['time_creation']
