"""Notifier object for sending alerts to Tasker via AutoRemote.

The object is designed to be used with the football_notify_service.py script.
As such, it implements a "Notify method"

"""
import requests


class AutoRemoteNotifier(object):
    """Class object to handle sending messages to AutoRemote.

    Class should be initialised by passing the specific key for the device you
    wish to notify.
    """

    def __init__(self, key, prefix):
        """Method to create an instance of the notifier.

        Takes two parameters:

        key:    AutoRemote key string
        prefix: prefix used by AutoRemote to identify the message
        """
        self.base = "http://autoremotejoaomgcd.appspot.com/sendmessage"
        self.key = key
        self.prefix = prefix

    def __getPage(self, url, params):
        """Boolean. Returns True if request sent successfully.

        For AutoRemote we expect the response to be "OK"."""
        r = requests.get(url, params=params)
        return r.status_code == 200 and r.content == "OK"

    def __formatMessage(self, event, matchobject):
        """Method to create string to be sent to AutoRemote."""
        return u"{} {}=:={}".format(self.prefix,
                                    event,
                                    unicode(matchobject))

    def Notify(self, event, matchobject, **kwargs):
        """Method to send message via Autoremote.

        Converts the match object into a string for sending to AutoRemote.

        Returns True if message sent successfully.
        """
        params = {"key": self.key,
                  "message": self.__formatMessage(event, matchobject)}
        return self.__getPage(self.base, params)
