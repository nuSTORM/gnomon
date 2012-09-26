"""Handle routing output, errors, and exceptions to disk and screen
"""
import logging
import sys
import time
import os
import uuid
import gnomon.Configuration as Configuration


def getLogLevels():
    "Return log levels that Python's logging facilities understands"
    return ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


def addLogLevelOptionToArgs(parser):
    """Add log level arguments to command line parser

    This is not in the schema because the log level needs to be known when
    setting up the Configuration classes
    """
    parser.add_argument('--log_level',
        choices=getLogLevels(),
        default='INFO')


class StreamToLogger(object):
    "Fake file-like stream object that redirects writes to a logger instance."

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


def setupLogging(console_level, name):
    config = Configuration.GLOBAL_CONFIG

    output_filename = 'gnomon_%s_%s.log' % (name, str(uuid.uuid4()))

    output_filename = os.path.join(config['log_dir'],
        output_filename)

    logging.basicConfig(filename=output_filename, mode='w',
        level=logging.DEBUG)

    console_handler = logging.StreamHandler(sys.__stdout__)
    console_handler.setLevel(console_level)
    formatter = logging.Formatter('%(levelname)s(%(name)s): %(message)s')
    console_handler.setFormatter(formatter)

    logger = logging.getLogger('root')
    logger.addHandler(console_handler)

    stdout_logger = logging.getLogger('root').getChild('STDOUT')
    sl = StreamToLogger(stdout_logger, logging.INFO)
    sys.stdout = sl

    stderr_logger = logging.getLogger('root').getChild('STDERR')
    sl = StreamToLogger(stderr_logger, logging.ERROR)
    sys.stderr = sl

    logger.info('Starting up Gnomon (PID: %d)', os.getpid())

    logger.info('Using log filename: %s', output_filename)

    logger.info('Start time: %s', time.ctime())
