import logging
import sys
import time
import os
import uuid

def getLogLevels():
    return ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

def addLogLevelOptionToArgs(parser):
    parser.add_argument('--log_level',
                        choices=getLogLevels(),
                        default='INFO')

class StreamToLogger(object):
    """                                                                                                                            
    Fake file-like stream object that redirects writes to a logger instance.                                                       
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


def setupLogging(console_level, name, logfileless=False):
    output_filename = 'log/gnomon_%s_%s.log' % (name, str(uuid.uuid4()))

    #if not logfileless:
    #    logging.basicConfig(filename=output_filename, mode='w', level=logging.DEBUG)

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

    if not logfileless:
        logger.info('Using log filename: %s', output_filename)
    else:
        logger.warning('No log file will be used')
        
    logger.info('Start time: %s', time.ctime())
