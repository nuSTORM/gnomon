"""Catologue processors
"""

from gnomon.processors.Digitizer import VlenfSimpleDigitizer
from gnomon.processors.Fitter import EmptyTrackFromDigits
from gnomon.processors.Fitter import ContinousLongitudinalLength
from gnomon.processors.Fitter import ExtractTracks
from gnomon.processors.Fitter import VlenfPolynomialFitter
from gnomon.processors.Fitter import ClassifyVariables
from gnomon.processors.Truth import AppendTruth
from gnomon.processors.DataManager import CouchManager


_processors = [VlenfSimpleDigitizer,
               EmptyTrackFromDigits,
               ContinousLongitudinalLength,
               ExtractTracks,
               VlenfPolynomialFitter,
               ClassifyVariables,
               AppendTruth,
               CouchManager]

# Build lookup table of class names to class objects
_proc_lookup = {}
for processor in _processors:
    _proc_lookup[processor.__name__] = processor

def lookupProcessor(name):
    if name in _proc_lookup:
        return _proc_lookup[name]
    else:
        raise LookupError("Unknown processor %s" % name)
