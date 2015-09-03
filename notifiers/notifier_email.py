"""Notifier object for sending alerts via email.

The object is designed to be used with the football_notify_service.py script.
As such, it implements a "Notify method"

"""
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import service.constants as CONST
from notifiers.notifierbase import NotifierBase
from notifiers.exceptions import InvalidNotifier

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


OUTER_TEMPLATE = (
  u"""<body><html>
  {body}
  </html></body>"""
)

MATCH_TEMPLATE = (
  u"""  <table width="100%">
    <tbody>
    <tr><td colspan="3" style="text-align: center;">{status}</td></tr>
    <tr>
    <td width="40%" style="text-align: center;">{hometeam}</td>
    <td width="20%"style="text-align: center;">{homescore}-{awayscore}</td>
    <td width="40%"style="text-align: center;">{awayteam}</td>
    </tr>
    <tr>
    <td width="40%" style="text-align: center;">{hsc}</td>
    <td width="20%"style="text-align: center;">{matchtime}</td>
    <td width="40%"style="text-align: center;">{asc}</td>
    </tr>
    </tbody>
    </table>"""
)


class EmailNotifier(NotifierBase):
    """Class object to handle sending messages via email.

    This is a generic class to handle sending via SMTP. It is included as a
    proof concept rather than a recommend option.

    Usernames and passwords are passed in plain text.

    More secure options may be available (e.g. using oauth2 for Gmail).
    """

    def __init__(self, server, port, username, password, fromaddr, toaddrs,
                 title=None):
        """Method to create an instance of the notifier.

        Takes six parameters:

        server:    server address (e.g. "smtp.gmail.com")
        port:      server port (e.g. 587)
        username:  username for account
        password:  password for account
        fromaddr:  sender of email
        toaddrs:   list of recipients ["foo@bar.com", "bar@foo.com"]
        title:     optional prefix for email subject line
        """
        NotifierBase.__init__(self)
        self.__serveraddr = server
        self.__port = port
        self.__username = username
        self.__password = password
        self.__fromaddr = fromaddr
        self.__toaddrs = toaddrs
        self.__title = "{title} ".format(title=title) if title else ""
        self._modes += CONST.MODE_LEAGUE

    def __createMatchTable(self, matchobject):
        m = matchobject
        if type(m.HomeScorers) == list:
            hsc = m.formatIncidents(m.HomeScorers, newline=True)
            hsc = hsc.replace("\n", "<br />")
        else:
            hsc = ""

        if type(m.AwayScorers) == list:
            asc = m.formatIncidents(m.AwayScorers, newline=True)
            asc = asc.replace("\n", "<br />")
        else:
            asc = ""
        table = MATCH_TEMPLATE.format(hsc=hsc, asc=asc, **m.matchdict)
        return table

    def __createMessage(self, body, plain, subject):
        """Method to create string to be sent via email."""
        msg = MIMEMultipart('alternative')
        msg.set_charset('utf8')

        msg['Subject'] = subject
        msg['From'] = self.__fromaddr
        msg['To'] = ", ".join(self.__toaddrs)

        html = OUTER_TEMPLATE.format(body=body)

        plainpart = MIMEText(plain.encode('utf-8'), "plain", _charset='utf-8')
        htmlpart = MIMEText(html.encode('utf-8'), "html", _charset='utf-8')

        msg.attach(plainpart)
        msg.attach(htmlpart)

        return msg

    def __formatMatch(self, event, matchobject):
        """Method to create string to be sent via email."""
        body = self.__createMatchTable(matchobject)
        plain = unicode(matchobject)
        subject = self.__getSubject(event, matchobject)

        return self.__createMessage(body, plain, subject)

    def __formatLeague(self, event, leagueobject):
        bodylist = []
        plainlist = []

        for m in leagueobject.LeagueMatches:
            bodylist.append(self.__createMatchTable(m))
            plainlist.append(unicode(m))

        body = "<br />".join(bodylist)
        plain = "\n".join(plainlist)

        return self.__createMessage(body, plain, leagueobject.LeagueName)

    def __getSubject(self, event, matchobject):
        """Provides a concise summary of the reason for the notification.

        Suitable to be used as subject line for an email.
        """
        score = (u"{hometeam} {homescore}-{awayscore} "
                 "{awayteam}".format(**matchobject.matchdict))

        prefix = PREFIXES.get(event, PRE_OTHER)

        return u"{title}{prefix} {score}".format(title=self.__title,
                                                 prefix=prefix,
                                                 score=score)

    def __sendMail(self, msg):
        """Sends the email. Requires one parameter:

        msg: MIMEMultipart object
        """

        success = False

        try:
            self.__server = smtplib.SMTP(self.__serveraddr, self.__port)
            self.__server.starttls()
            self.__server.ehlo()
            self.__server.login(self.__username, self.__password)
            self.__server.sendmail(self.__fromaddr,
                                   self.__toaddrs,
                                   msg.as_string())
            success = True
        except SMTPException:
            success = False
        finally:
            self.__server.quit()
            return success

    def Notify(self, event, matchobject, **kwargs):
        """Method to send message via email.

        Returns True if message sent successfully.
        """
        mode = kwargs.get("mode", CONST.MODE_MATCH)
        result = False

        if mode == CONST.MODE_MATCH:
            msg = self.__formatMatch(event, matchobject)
        elif mode == CONST.MODE_LEAGUE:
            msg = self.__formatLeague(event, matchobject)

        if msg:
            result = self.__sendMail(msg)

        return result
