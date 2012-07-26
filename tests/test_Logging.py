from unittest import TestCase
import sys
import argparse
import exceptions

import logging  # python's
import Logging  # gnomon's


class TestLogging(TestCase):
    def setUp(self):
        pass

    def test_exist_getLogLevels(self):
        bad_level_name = 'blarg'
        l = logging.getLogger(bad_level_name)

        with self.assertRaises(ValueError):
            l.setLevel(bad_level_name)

        for level_name in Logging.getLogLevels():
            l = logging.getLogger(level_name)
            l.setLevel(level_name)

    def test_setupLogging(self):
        Logging.setupLogging('WARNING', 'testname')

        self.assertNotEqual(sys.stdout, sys.__stdout__)
        self.assertNotEqual(sys.stderr, sys.__stderr__)

    def test_StreamToLogger(self):
        pass  # can't think of test, wait for bugs

    def test_addLogLevelOptionToArgs(self):
        for level_name in Logging.getLogLevels():
            parser = argparse.ArgumentParser()
            with self.assertRaises(exceptions.SystemExit):
                parser.parse_args(['--log_level', level_name])

            Logging.addLogLevelOptionToArgs(parser)

            with self.assertRaises(exceptions.SystemExit):
                parser.parse_args(['--log_level'])

            parser.parse_args(['--log_level', level_name])
