#!/usr/bin/env python
"""Live Football Scores Notification Service

by elParaguayo

The script checks football scores and sends updates to a notifier which
can be handled by the user as they see fit (e.g. notifications for goals).

An Issues/To Do list will be maintained separately on GitHub at this address:
https://github.com/elParaguayo/football_notifications/issues

Any errors can be discussed on the Raspberry Pi forum at this address:
https://www.raspberrypi.org/forums/viewtopic.php?f=41&t=118203

Version: 0.1
"""

import logging

from service.scoresservice import ScoreNotifierService
from notifiers.notifier_autoremote import AutoRemoteNotifier
from notifiers.notifier_email import EmailNotifier

##############################################################################
# USER SETTINGS - CHANGE AS APPROPRIATE                                      #
##############################################################################

# myTeams: list of the teams for which you want to receive updates.
# NB the team name needs to match the name used by the BBC
myTeams = ["Chelsea", "Arsenal"]

# LIVE_UPDATE_TIME: Time in seconds until data refreshes while match is live
# NON_LIVE_UPDATE_TIME: Time in seconds until data refreshes after match or
#                       when there is no match on the day
# NB. Once a match is found, the script will try to sleep until 5 minutes
# before kick-off
LIVE_UPDATE_TIME = 30
NON_LIVE_UPDATE_TIME = 60 * 60

# DETAILED - Request additional information on match (e.g. goalscorers)
# Should be updated to reflect the needs of the specific notifier
DETAILED = True

# LOGFILE:
LOGFILE = "/home/pi/service.log"

# DEBUG_LEVEL: set the log level here
# logging.DEBUG: Very verbose. Will provide updates about everything. Probably
#                best left to developers
# logging.INFO:  Reduced info. Just provides updates for errors and
#                notification events
# logging.ERROR: Just provide log info when an error is encountered.
DEBUG_LEVEL = logging.ERROR

##############################################################################
# NOTIFIERS - You should only initialise one notifier and comment out the    #
# other. Future versions may allow for multiple notifiers                    #
##############################################################################

# E-MAIL #####################################################################

# FROMADDR - string representing sender
FROMADDR = 'Football Score Service'
# TOADDR - list of recipients
TOADDR = ['foo@bar.com']
# USER - username for mail account
USER = 'foobar@gmail.com'
# PWD - password
PWD = 'password'
# SERVER - address of mail server
SERVER = 'smtp.gmail.com'
# PORT - mail server port number
PORT = 587
# TITLE - optional prefix for email subject line
TITLE = ""

notifier = EmailNotifier(SERVER, PORT, USER, PWD, FROMADDR, TOADDR, TITLE)

# AUTOREMOTE #################################################################

# myAutoRemoteKey - long string key used in web requests for AutoRemote
myAutoRemoteKey = ""

# prefix - single word used by AutoRemote/Tasker to identify notifications
prefix = "scores"

# notifier = AutoRemoteNotifier(myAutoRemoteKey, prefix)

##############################################################################
# DO NOT CHANGE ANYTHING BELOW THIS LINE                                     #
##############################################################################

# Create a logger object for providing output.
logger = logging.getLogger("ScoresService")
logger.setLevel(DEBUG_LEVEL)

# Tell the logger to use our filepath
fh = logging.FileHandler(LOGFILE)
fh.setLevel(DEBUG_LEVEL)

# Set the format for our output
formatter = logging.Formatter('%(asctime)s: '
                              '%(levelname)s: %(message)s',
                              datefmt="%d/%m/%y %H:%M:%S")
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.debug("Logger initialised.")

if __name__ == "__main__":

    try:
        logger.debug("Initialising service...")
        for team in myTeams:
            service = ScoreNotifierService(team,
                                           notifier=notifier,
                                           livetime=LIVE_UPDATE_TIME,
                                           nonlivetime=NON_LIVE_UPDATE_TIME,
                                           handler=fh,
                                           level=DEBUG_LEVEL,
                                           detailed=DETAILED)
            logger.debug("Starting thread for {}".format(team))
            service.daemon = True
            service.start()

    except KeyboardInterrupt:
        logger.error("User exited with ctrl+C.")

    except:
        # We want to catch error messages
        logger.exception("Exception encountered. See traceback message.\n"
                         "Please help improve development by reporting"
                         " errors.")
        raise
