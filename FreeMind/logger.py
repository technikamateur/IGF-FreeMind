import logging
from logging.handlers import SMTPHandler
import time
from FreeMind import config
from FreeMind.models import LogMessage
from FreeMind import db

# Patch SMTPHandler to allow only a certain frequency
class _SMTPHandler(SMTPHandler):
    lastMail = False;

    def getSubject(self, record):
        formatter = logging.Formatter(fmt=self.subject)
        return formatter.format(record)

    def emit(self, record):
        now = time.time()
        if not self.lastMail or (now - self.lastMail) > config.mail['interval']:
            super(_SMTPHandler, self).emit(record)
            self.lastMail = now;

# A Simple Logging Handler for the Database
class SQLHanlder(logging.StreamHandler):
    def emit(self, record):
        logMessage = LogMessage(record.levelname, self.format(record))
        db.session.add(logMessage)
        db.session.commit()


# Set up Logging and Levels
logger = logging.getLogger('SERVER');
logger.setLevel(logging.DEBUG);

# Formatter
__formatter = logging.Formatter('\033[1m%(asctime)s - %(name)s - %(levelname)s - %(message)s \033[21m')

# Add multiple Mail Handlers for Levels
for level in config.mail['mailAdresses']:
    if len(config.mail['mailAdresses'][level]) == 0:
        continue

    __handler = _SMTPHandler(config.mail['mailServer']['host'],
                            '<server@' + config.mail['mailServer']['host'] + '> FreeMind', # TODO: Add to Config
                            config.mail['mailAdresses'][level],
                            subject=config.mail['subjectLine'],
                            credentials=(config.mail['mailServer']['username'],
                                         config.mail['mailServer']['password']))

    __handler.setLevel(level)
    logger.addHandler(__handler)

__sqlHandler = SQLHanlder()
__sqlHandler.setLevel(logging.INFO)
logger.addHandler(__sqlHandler)

__streamHandler = logging.StreamHandler()
__streamHandler.setLevel(logging.ERROR)
logger.addHandler(__streamHandler)

__streamHandler.setFormatter(__formatter)
