"""Live Football Scores Notification Service

by elParaguayo

This module provides the main ScoreNotifierService class which handles the
checking of scores and sending updates to the relevant notifier.
"""
import sys
from time import sleep
import logging
import socket
import threading

from service.footballscores import League
from service.servicebase import ServiceBase
import service.constants as CONST


class LeagueNotifierService(ServiceBase):
    """Class object to check football scores and send updates via AutoRemote.

    Each instance of this class can only process one team.

    While multiple teams could theoretically be handled by multiple instances
    of this class, it is not recommended as there would be no sharing of data
    between instances, resulting in increased number of http requests.

    Due to the blocking sleep call used in the class, multiple instances
    should be created in separate threads.

    Class is initialised by passing the name of the team and the key for the
    AutoRemote service.

    e.g. myservice = ScoreNotifierService("Chelsea", "long_autoremote_key")

    The "detailed" parameter should not be passed for now. This is for future
    updates.
    """

    def __init__(self, league, notifiers=None, detailed=False, handler=None,
                 livetime=60, nonlivetime=3600, level=logging.ERROR):
        """Method to create an instance of the notifier service object.

        Currently take six (four are optional) parameters:

          team:        name of the team for which updates are required
          notifiers:   object capable of acting as a notifier
          detailed:    (optional) request additional detail (not implemented)
          handler:     handler object for debug logs
          level:       debug level
          livetime:    number of seconds before refresh when match in progress
          nonlivetime: number of seconds before refresh when no live match

        NB initialising the object does not begin the service. The "run"
        method must be called separately.
        """
        # Most of the set up is handled by the ServiceBase class so let's
        # initialise that first.
        ServiceBase.__init__(self, notifiers=notifiers, detailed=detailed,
                             handler=handler, livetime=livetime,
                             nonlivetime=nonlivetime, level=level,
                             loggerid=league, servicemode=CONST.MODE_LEAGUE)

        # Now we can do some stuff that's purely relevant for the football
        # match score service.
        self.leagueid = league
        self._debug("Starting service with league: {}".format(self.leagueid))
        self.detailed = detailed

    def run(self):
        """Method to start the notification service.

        There is no error handling at this level. If the user wants to restart
        the service automatically, then the "run" method should be placed in a
        try... except... block as appropriate.
        """

        # Create an instance of the League
        self.league = League(self.leagueid, detailed=self.detailed)

        # Service starts here...
        try:

            while True:

                # If the script has found any matches then we need to
                # process it to see if we need any notifications
                self._debug("Checking status...")
                if self.league.LeagueMatches:
                    self._checkStatus()
                else:
                    self._debug("No matches found.")

                # Once we've processed the football match we need to sleep for
                # a while.
                self._debug("Calculating sleep time...")
                self._sleep()

                # After that it's time to refresh the data
                self._debug("Refreshing data...")
                self._update()

        except:
            self._exception("Exception encountered in thread.\n"
                            "Please help improve the script by reporting.")
            raise

    def _sendUpdate(self, code):
        """Method to send notifications.

        Needs one parameter:

          code:    prefix used to identify event type
        """
        with self._lock:
            self._debug("Sending update: {}".format(code))
            for notifier in self._notifiers:
                r = notifier.Notify(code, self.league, mode=self.servicemode)
                self.checkNotification(r)

    def _checkStatus(self):
        """Method to process a football match and send notifications where
        certain events are triggered.
        """

        # New football match found. Only triggers once per match so user gets
        # a notification that there is a game today. Subsequent notifications
        # will only be sent to the extent one of the conditions below matches.
        if self.league.NewMatch:
            self._info("Match found.")
            self._sendUpdate(CONST.STATUS_MATCH_FOUND)

        # Goooooooooooooooooaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaallll!
        elif self.league.Goal:
            self._info("Goal.")
            code = CONST.LEAGUE_GOAL
            self._sendUpdate(code)

        # Status change e.g. start of match, half time, full time.
        elif self.league.StatusChanged:
            self._info("Status change.")
            code = CONST.LEAGUE_STATUS_CHANGE
            self._sendUpdate(code)

    def _sleep(self):
        """Method to calculate required sleep time depending on status of
        football match.
        """

        # There's currently no football match found, so there's no need for an
        # update for a while.
        if not self.league.LeagueMatches:
            self._debug("No match.")
            delay = self._nonlivetime

        # There is a football match, but it hasn't started yet.
        elif not self.league.HasStarted:
            self._debug("League hasn't started")

            # Get kickoff time and then calculate number of seconds required
            # until approximately 5 minutes before kickoff (at which point it
            # switches to regular updates)
            kickoff = min((m.TimeToKickOff.total_seconds()
                           for m in self.league.LeagueMatches))
            if kickoff < 300:
                delay = self._livetime
            else:
                delay = kickoff - 240

        # Match is over so need for regular updates now.
        elif self.league.HasFinished:
            self._debug("League has finished")
            delay = self._nonlivetime

        # Match is live so we need regular updates
        elif self.league.IsLive:
            self._debug("League is in progress")
            delay = self._livetime

        # I can't think of any reason for this to be triggered, but better to
        # have this here just in case!
        else:
            self._debug("Not sure why we're here!")
            delay = self._nonlivetime

        # Time to sleep.
        self._debug("Sleeping for {} seconds".format(delay))
        sleep(delay)

    def _update(self):
        """Method to refresh football match."""

        self.league.Update()
