"""Notifier object template

The object is designed to be used as a basis for custom notifier classes.

"""

# This imports the event types used by the service and ensures consistency
# across notifiers.
import service.constants as CONST

# Constants are as follows:
# CONST.GOAL_MYTEAM - Called when the selected team scores
# CONST.GOAL_OPPOSITION - called when the opposition team scores
# CONST.STATUS_MATCH_FOUND - called when the service find a new match. Only
#                            called once per match.
# CONST.STATUS_KICK_OFF - called when play starts (either half)
# CONST.STATUS_HALF_TIME - called at start of half time
# CONST.STATUS_FULL_TIME - called at full time


class TemplateNotifier(object):
    """Description of notifier goes here."""

    def __init__(self, **kwargs):
        """Method to create an instance of the notifier.

        NB The notifier will be initialised before the service starts.
        """
        pass

    def Notify(self, event, matchobject):
        """This is the method that will be called by the service when an
        event is triggered. As such the name and parameters cannot be changed.

        event:       One of the constants set out above.
        matchobject: FootballMatch object. There is a lot of information
                     available. Have a look at the service.footballscores.py
                     source for details.

        Should return True if event notification was successful.
        """
        return True
