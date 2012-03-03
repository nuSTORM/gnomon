from unittest import TestCase
from subprocess import check_output

MY_COMMANDS = ['clhep', 'geant4', 'root']
MY_ARGS = ['prefix', 'libs', 'cflags']

class TestShepherdConfig(TestCase):
    def setUp(self):
        self._command_name = 'shepherd-config'

    def test_doesthiswor(self):
        for command in MY_COMMANDS:
            for arg in MY_ARGS:
                print check_output([self._command_name, '--%s' % command, '--%s' % arg])
        

