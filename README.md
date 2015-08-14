**Live Football Scores Notification Service**

*Description of service*

This script is designed to be run as a headless service. The script periodically checks for live matches and, if it finds a match involving the preset team, sends live updates (e.g. kick-off, goals etc.).

The script is designed to be customisable. Notifications are handled by "notifiers". The script currently has two available notifiers, email and AutoRemote. However, additional notifiers could be created e.g. if you had an LED strip attached to your RaspberryPi then you could have it flash whenever a goal was scored. A template notifier class is included with notes as to how it reacts to alerts from the service.

*Installation*

Sadly, I have no experience of writing installation scripts so there isn't one included here. That means that, currently, some effort is required from users.

1. Clone the latest version of this repository
2. Make sure main.py is executable
3. Move scores_service to `/etc/init.d/` and make sure it is executable
4. Run `sudo update-rc.d scores_service defaults`

*Configuration*

1. Open scores_service and edit the path to match the location of the script.
2. If necessary, change the user as which the script should be run. If you're using GPIO in a custom notifier, you may need to change this to root.
3. Open main.py and change the configurations details as per the instructions.

*Running*

1. Assuming everything's configured OK, it should just be a case of `sudo /etc/init.d/scores_service start`

*Issues/bugfixes/feature requests*

All of the above should be reported in the RaspberryPi forum. However, users are free/encouraged to fork the code and submit pull requests.
