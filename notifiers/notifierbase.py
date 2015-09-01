from service import constants as CONST
from notifiers.exceptions import InvalidNotifier


class NotifierBase(object):
    def __init__(self):
        # This should be updated if other modes can be handled.
        # New modes are ADDED as checking should be done by bitwise
        # calculations e.g.
        #     if self._modes & CONST.MODE_LEAGUE:
        #       do_something_for_leagues_here()
        self._modes = CONST.MODE_MATCH

    def checkMode(self, mode):
        if not mode & self._modes:
            raise InvalidNotifier("The selected notifier is incompatible "
                                  "with the requested mode "
                                  "({mode}).".format(mode=mode))
