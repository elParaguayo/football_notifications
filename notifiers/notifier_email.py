"""Notifier object for sending alerts via email.

The object is designed to be used with the football_notify_service.py script.
As such, it implements a "Notify method"

"""
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import service.constants as CONST

PRE_NEW_MATHCH = "New match found."
PRE_KICK_OFF = "KICK-OFF!"
PRE_HALF_TIME = "HALF TIME!"
PRE_FULL_TIME = "FULL TIME!"
PRE_TEAM_GOAL = "GOOOOOOAAAAALLL!!!"
PRE_OPPOSITION_GOAL = "Uh oh..."

MATCH_TEMPLATE = (
  u"""<body><html>
  <table width="100%">
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
  </table>
  </html></body>"""
)


class EmailNotifier(object):
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
        self.__serveraddr = server
        self.__port = port
        self.__username = username
        self.__password = password
        self.__fromaddr = fromaddr
        self.__toaddrs = toaddrs
        self.__title = "{title} ".format(title=title) if title else ""

    def __formatMessage(self, event, matchobject):
        """Method to create string to be sent via email."""
        msg = MIMEMultipart('alternative')
        msg.set_charset('utf8')

        msg['Subject'] = self.__getSubject(event, matchobject)
        msg['From'] = self.__fromaddr
        msg['To'] = ", ".join(self.__toaddrs)

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

        html = MATCH_TEMPLATE.format(hsc=hsc, asc=asc, **m.matchdict)
        plain = unicode(m)

        plainpart = MIMEText(plain.encode('utf-8'), "plain", _charset='utf-8')
        htmlpart = MIMEText(html.encode('utf-8'), "html", _charset='utf-8')

        msg.attach(plainpart)
        msg.attach(htmlpart)

        return msg

    def __getSubject(self, event, matchobject):
        """Provides a concise summary of the reason for the notification.

        Suitable to be used as subject line for an email.
        """
        score = ("{hometeam} {homescore}-{awayscore} "
                 "{awayteam}".format(**matchobject.matchdict))

        if event == CONST.STATUS_MATCH_FOUND:
            prefix = PRE_NEW_MATHCH

        elif event == CONST.STATUS_KICK_OFF:
            prefix = PRE_KICK_OFF

        elif event == CONST.STATUS_HALF_TIME:
            prefix = PRE_HALF_TIME

        elif event == CONST.STATUS_FULL_TIME:
            prefix = PRE_FULL_TIME

        elif event == CONST.GOAL_MYTEAM:
            prefix = PRE_TEAM_GOAL

        elif event == CONST.GOAL_OPPOSITION:
            prefix = PRE_OPPOSITION_GOAL

        return u"{title}{prefix} {score}".format(title=self.__title,
                                                 prefix=prefix,
                                                 score=score)

    def __sendMail(self, msg):
        """Sends the email. Requires one parameter:

        msg: MIMEMultipart object
        """

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

    def Notify(self, event, matchobject, *kwargs):
        """Method to send message via email.

        Returns True if message sent successfully.
        """
        return self.__sendMail(self.__formatMessage(event, matchobject))
