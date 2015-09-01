import threading
import logging


class ServiceBase(threading.Thread):

    def __init__(self, notifier=None, detailed=False, handler=None,
                 livetime=60, nonlivetime=3600, level=logging.ERROR,
                 loggerid=None):
        """Method to create an instance of the base service object.

        Currently take six (four are optional) parameters:

          team:        name of the team for which updates are required
          notifier:    object capable of acting as a notifier
          detailed:    (optional) request additional detail (not implemented)
          handler:     handler object for debug logs
          level:       debug level
          livetime:    number of seconds before refresh when match in progress
          nonlivetime: number of seconds before refresh when no live match

        NB initialising the object does not begin the service. The "run"
        method must be called separately.
        """
        threading.Thread.__init__(self)
        self._lock = threading.Lock()
        self._handler = handler
        self._level = level
        self._loggerid = loggerid
        self._logger = self._createLogger()
        self._can_log = self._logger is not None
        self.detailed = detailed
        self._notifier = notifier
        self._livetime = livetime
        self._nonlivetime = nonlivetime

    def _createLogger(self):
        logger = logging.getLogger("Worker({})".format(self._loggerid))
        logger.setLevel(self._level)
        logger.addHandler(self._handler)
        return logger

    def _debug(self, message):
        """Method for handling debugging messages."""
        if self._can_log:
            self._logger.debug(message)

    def _info(self, message):
        """Method for handling info messages."""
        if self._can_log:
            self._logger.info(message)

    def _error(self, message):
        """Method for handling error messages."""
        if self._can_log:
            self._logger.error(message)

    def _exception(self, message):
        """Method for handling exception messages."""
        if self._can_log:
            self._logger.exception(message)
