"""These constants should be used by the notification service and the notifier
to process updates.
"""

GOAL_MYTEAM = "goodgoal"
GOAL_OPPOSITION = "badgoal"
STATUS_MATCH_FOUND = "found"
STATUS_KICK_OFF = "L"
STATUS_HALF_TIME = "HT"
STATUS_FULL_TIME = "FT"

# League specific flags
LEAGUE_GOAL = "leaguegoal"
LEAGUE_STATUS_CHANGE = "leaguestatus"

# Mode flags to help notifiers know how to deal with message
MODE_MATCH = 1
MODE_LEAGUE = 2
