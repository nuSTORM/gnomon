"""Catologue processors such that they can be imported

TODO: Cleanup by using '__all__'?
#http://stackoverflow.com/questions/1057431/loading-all-modules-in-a-folder-in-python/1057534#1057534 ??
"""

from gnomon.processors.Digitizer import VlenfSimpleDigitizer
from gnomon.processors.Fitter import EmptyTrackFromDigits
from gnomon.processors.Fitter import CombineViews
from gnomon.processors.Fitter import ExtractTracks
from gnomon.processors.Fitter import VlenfPolynomialFitter
from gnomon.processors.Fitter import ClassifyVariables
from gnomon.processors.Truth import AppendTruth
from gnomon.processors.DataManager import CouchManager
from gnomon.processors.Filter import SaveInteresting
from gnomon.processors.Filter import AppearanceCuts
from gnomon.processors.Fiducial import FiducialCuts
from gnomon.processors.CreateROOTFile import CreateROOTDigitizedHits

_processors = [VlenfSimpleDigitizer,
               EmptyTrackFromDigits,
               CombineViews,
               ExtractTracks,
               VlenfPolynomialFitter,
               ClassifyVariables,
               AppendTruth,
               CouchManager,
               AppearanceCuts,
               SaveInteresting,
               FiducialCuts,
               CreateROOTDigitizedHits]

# Build lookup table of class names to class objects
_proc_lookup = {}
for processor in _processors:
    _proc_lookup[processor.__name__] = processor


def lookupProcessor(name):
    """Lookup processor class object by its name"""
    if name in _proc_lookup:
        return _proc_lookup[name]
    else:
        error_string = 'If you are creating a new processor, please read the\
documentation on creating a new processor'
        raise LookupError("Unknown processor %s\n%s" % (name, error_string))
