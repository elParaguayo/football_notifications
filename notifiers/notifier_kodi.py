"""Notifier object for sending alerts to Kodi.

The object is designed to be used with the football_notify_service.py script.
As such, it implements a "Notify method"

"""
import requests
import base64
import json

import service.constants as CONST

PRE_NEW_MATHCH = "New match found."
PRE_KICK_OFF = "KICK-OFF!"
PRE_HALF_TIME = "HALF TIME!"
PRE_FULL_TIME = "FULL TIME!"
PRE_TEAM_GOAL = "GOOOOOOAAAAALLL!!!"
PRE_OPPOSITION_GOAL = "Uh oh..."

# This shouldn't be needed, but let's have it just in case.
PRE_OTHER = "Unknown status"

# Lookup to match events to the desred prefix.
PREFIXES = {CONST.GOAL_MYTEAM: PRE_TEAM_GOAL,
            CONST.GOAL_OPPOSITION: PRE_OPPOSITION_GOAL,
            CONST.STATUS_MATCH_FOUND: PRE_NEW_MATHCH,
            CONST.STATUS_KICK_OFF: PRE_KICK_OFF,
            CONST.STATUS_HALF_TIME: PRE_HALF_TIME,
            CONST.STATUS_FULL_TIME: PRE_FULL_TIME}


class KodiNotifier(object):
    """Class object to handle sending messages to AutoRemote.

    Class should be initialised by passing the specific key for the device you
    wish to notify.
    """

    def __init__(self, address, port, username=None, pwd=None,
                 displaytime=5000):
        """Method to create an instance of the notifier.

        Takes four parameters:

        address:     address of Kodi instance
        port:        prefix used by AutoRemote to identify the message
        username:    username to access Kodi
        pwd:         password
        displaytime: time in miliseconds to show notification
        """
        self.base = "http://{address}:{port}/jsonrpc".format(address=address,
                                                             port=port)
        self.username = username
        self.password = pwd
        self.id = 0

    def __getPage(self, url, params):
        """Boolean. Returns True if request sent successfully.

        For AutoRemote we expect the response to be "OK"."""
        headers = {'Content-Type': 'application/json'}

        # Use HTTP authentication from
        # http://forum.xbmc.org/showthread.php?tid=127759&pid=1346728#pid1346728
        if self.password is not None and self.username is not None:
            auth = '{{user}:{pwd}}'.format(user=self.username,
                                           pwd=self.password)
            base64string = base64.encodestring(auth)
            base64string = base64string.replace('\n', '')
            headers['Authorization'] = 'Basic %s' % (base64string)

        r = requests.post(url, data=json.dumps(params), headers=headers)
        result = json.loads(r.content)

        return r.status_code == 200 and result.get("result", False) == "OK"

    def __formatMessage(self, event, matchobject):
        """Method to create the notification to be sent to Kodi."""
        params = {"title": PREFIXES.get(event, PRE_OTHER),
                  "message": str(matchobject)}

        return params

    def Notify(self, event, matchobject, **kwargs):
        """Method to send message via Autoremote.

        Converts the match object into a string for sending to AutoRemote.

        Returns True if message sent successfully.
        """
        params = {}
        params['jsonrpc'] = '2.0'
        params['id'] = self.id
        self.id += 1
        params['method'] = "GUI.ShowNotification"
        params['params'] = self.__formatMessage(event, matchobject)

        return self.__getPage(self.base, params)
