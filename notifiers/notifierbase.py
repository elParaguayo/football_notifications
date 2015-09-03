from service import constants as CONST


class NotifierBase(object):
    def __init__(self):
        # This should be updated if other modes can be handled.
        # New modes are ADDED as checking should be done by bitwise
        # calculations e.g.
        #     if self._modes & CONST.MODE_LEAGUE:
        #       do_something_for_leagues_here()
        # This assumes that a new notifier will handle match notifications.
        # If this is not the case then this should be reset.
        self._modes = CONST.MODE_MATCH

    def checkMode(self, mode):
        """Checks whether a notifier is compatible with the selected mode.

        Returns True or False as appropriate.
        """
        return bool(mode & self._modes)

    def __str__(self):
        """Simple method to get class name (useful for logging purposes)."""
        return self.__class__.__name__
