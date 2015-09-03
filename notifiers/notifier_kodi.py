"""Notifier object for sending alerts to Kodi.

The object is designed to be used with the football_notify_service.py script.
As such, it implements a "Notify method"

"""
import requests
import base64
import json
import socket

import service.constants as CONST
from notifiers.notifierbase import NotifierBase

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


class KodiNotifier(NotifierBase):
    """Class object to handle sending messages to Kodi.

    Class should be initialised by passing the specific key for the device you
    wish to notify.
    """

    def __init__(self, kodis, displaytime=5000):
        """Method to create an instance of the notifier.

        Takes two parameters:

        kodis:       List of kodi machines to notify. Each machine should be a
                     dict as follows:

                     address:  IP address of Kodi machine (e.g. "192.168.0.2"
                               or "localhost")
                     port:     Port that Kodi is listening on, usually 8080
                     username: username if one set
                     password: password if one set

        displaytime: Amount of time (in milliseconds) to display notification
        """
        NotifierBase.__init__(self)
        self.base = "http://{address}:{port}/jsonrpc"

        # If user has passed a single dict then we need to put it in a list
        if type(kodis) == dict:
            self.kodis = [kodis]
        else:
            self.kodis = kodis

        self.id = 0
        self.displaytime = displaytime

    def __getPage(self, kodi, params):
        """Boolean. Returns True if request sent successfully.

        For Kodi, we need to look for an OK message in the JSON response.
        """
        headers = {'Content-Type': 'application/json'}

        # Use HTTP authentication from
        # http://forum.xbmc.org/showthread.php?tid=127759&pid=1346728#pid1346728
        username = kodi.get("username", None)
        password = kodi.get("password", None)
        if username and password:
            auth = '{{user}:{pwd}}'.format(user=username,
                                           pwd=password)
            base64string = base64.encodestring(auth)
            base64string = base64string.replace('\n', '')
            headers['Authorization'] = 'Basic %s' % (base64string)

        url = self.base.format(address=kodi["address"],
                               port=kodi.get("port", 8080))

        try:
            r = requests.post(url,
                              data=json.dumps(params),
                              headers=headers,
                              timeout=2)

            result = json.loads(r.content)

            return r.status_code == 200 and result.get("result", False) == "OK"

        except (socket.timeout, requests.Timeout, requests.ConnectionError):

            return False

    def __formatMessage(self, event, matchobject):
        """Method to create the notification to be sent to Kodi."""
        params = {"title": PREFIXES.get(event, PRE_OTHER),
                  "message": str(matchobject),
                  "displaytime": self.displaytime}

        return params

    def Notify(self, event, matchobject, **kwargs):
        """Method to send notifications to Kodi

        Converts the match object into a JSON RPC call and sends to each
        Kodi instance.

        Returns True if message sent successfully.
        """
        success = []

        params = {}
        params['jsonrpc'] = '2.0'
        params['method'] = "GUI.ShowNotification"
        params['params'] = self.__formatMessage(event, matchobject)

        for kodi in self.kodis:
            params['id'] = self.id
            self.id += 1
            success.append(self.__getPage(kodi, params))

        return all(success)
""
