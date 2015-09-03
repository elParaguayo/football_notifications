import logging
from time import sleep

import service.constants as CONST
from service.scoresservice import ScoreNotifierService
from service.leagueservice import LeagueNotifierService


class FootballNotify(object):

    def __init__(self, teams, leagues, notifiers, livetime, nonlivetime,
                 level, detailed, logpath):

        self.teams = teams
        self.leagues = leagues
        self.notifiers = notifiers
        self.livetime = livetime
        self.nonlivetime = nonlivetime
        self.level = level
        self.detailed = detailed
        self.logpath = logpath
        self.matchnotifiers = self.getCompatibleNotifiers(CONST.MODE_MATCH)
        self.leaguenotifiers = self.getCompatibleNotifiers(CONST.MODE_LEAGUE)

        # Create a logger object for providing output.
        self.logger = logging.getLogger("ScoresService")
        self.logger.setLevel(self.level)

        # Tell the logger to use our filepath
        self.fh = logging.FileHandler(self.logpath)
        self.fh.setLevel(self.level)

        # Set the format for our output
        formatter = logging.Formatter('%(asctime)s '
                                      '%(levelname)s %(name)s: %(message)s',
                                      datefmt="%d/%m/%y %H:%M:%S")
        self.fh.setFormatter(formatter)
        self.logger.addHandler(self.fh)
        self.logger.debug("Logger initialised.")

    def getCompatibleNotifiers(self, mode):
        return [x for x in self.notifiers[:] if x.checkMode(mode)]

    def startMatchService(self, team):
        try:
            service = ScoreNotifierService(team,
                                           notifiers=self.matchnotifiers,
                                           livetime=self.livetime,
                                           nonlivetime=self.nonlivetime,
                                           handler=self.fh,
                                           level=self.level,
                                           detailed=self.detailed)
            self.logger.debug("Starting thread for {}".format(team))
            service.daemon = True
            service.start()
        except:
            self.logger.exception("Error starting "
                                  "match service ({})".format(match))
            raise

    def startLeagueService(self, leagueid):
        try:
            service = LeagueNotifierService(leagueid,
                                            notifiers=self.leaguenotifiers,
                                            livetime=self.livetime,
                                            nonlivetime=self.nonlivetime,
                                            handler=self.fh,
                                            level=self.level,
                                            detailed=self.detailed)
            self.logger.debug("Starting thread for league {}".format(leagueid))
            service.daemon = True
            service.start()

        except:
            self.logger.exception("Error starting "
                                  "league service ({})".format(leagueid))
            raise

    def run(self):

        self.logger.debug("Initialising services...")

        if self.teams and not self.matchnotifiers:
            self.logger.error("No compatible notifiers found for matches.\n"
                              "No match services will be started.")
        else:
            for team in self.teams:
                self.startMatchService(team)

        if self.leagues and not self.leaguenotifiers:
            self.logger.error("No compatible notifiers found for leagues.\n"
                              "No league services will be started.")
        else:
            for league in self.leagues:
                self.startLeagueService(league)

        try:
            while True:
                # Loop to keep the script running
                sleep(1)

        except KeyboardInterrupt:
            self.logger.error("User exited with ctrl+C.")

        except:
            # We want to catch error messages
            self.logger.exception("Exception encountered. See traceback"
                                  " message.\nPlease help improve development"
                                  " by reporting errors.")
            raise
