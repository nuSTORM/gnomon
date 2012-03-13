#!/usr/bin/env python
# system libraries
import sys
import argparse
import logging
import os
import random

# gnomon
import Configuration
import Logging
import Fitter

log = None  #  Logger for this file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='fit digits at the VLENF')
    parser.add_argument('--name', '-n', help='DB in CouchDB for output',
                        type=str, required=True)
    parser.add_argument('--logfileless', action='store_true',
                        help='this will disable writing out a log file')
    parser.add_argument('--run', help='run number',
                        type=int, required=True)

    Logging.addLogLevelOptionToArgs(parser)  #  adds --log_level
    args = parser.parse_args()

    Logging.setupLogging(args.log_level, args.name, logfileless=args.logfileless)
    log = logging.getLogger('root')
    log.debug('Commandline args: %s', str(args))

    random.seed()

    Configuration.run  = args.run
    Configuration.name = args.name
    
    config = Configuration.CouchConfiguration(warn_if_exists = True)
    db = config.getCurrentDB()

    fitter = Fitter.VlenfPolynomialFitter()
    fitter.Process()
    fitter.bulkCommit(True)